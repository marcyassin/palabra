package main

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"
	"strings"

	"github.com/google/uuid"
	"github.com/minio/minio-go/v7"
)

func (app *application) home(w http.ResponseWriter, r *http.Request) {
	if r.URL.Path != "/" {
		app.notFound(w)
		return
	}
	w.Header().Set("Content-Type", "text/plain; charset=utf-8")
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Palabra API Service"))
}

func (app *application) apiRoot(w http.ResponseWriter, r *http.Request) {
	if r.URL.Path != "/api" {
		app.notFound(w)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	w.Write([]byte(`{
		"service": "Palabra API",
		"version": "v1",
		"endpoints": {
			"books": "/api/books",
			"upload": "/api/books/upload"
		}
	}`))
}

func (app *application) getBook(w http.ResponseWriter, r *http.Request, bookId uuid.UUID) {
	book, err := app.books.Get(bookId)
	if err != nil {
		app.serverError(w, err)
		return
	}

	if book == nil {
		app.clientError(w, http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(book)
}

func (app *application) getBooks(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		w.Header().Set("Allow", http.MethodGet)
		app.clientError(w, http.StatusMethodNotAllowed)
		return
	}

	books, err := app.books.Latest(20)
	if err != nil {
		app.serverError(w, err)
		return
	}

	js, err := json.MarshalIndent(map[string]interface{}{
		"books": books,
	}, "", "  ")
	if err != nil {
		app.serverError(w, err)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	w.Write(js)
}

func (app *application) uploadBook(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		w.Header().Set("Allow", http.MethodPost)
		app.clientError(w, http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20) // 10 MB max memory
	if err != nil {
		app.clientError(w, http.StatusBadRequest)
		return
	}

	file, header, err := r.FormFile("file")
	if err != nil {
		app.clientError(w, http.StatusBadRequest)
		return
	}
	defer file.Close()

	language := r.FormValue("language")
	userIDStr := r.FormValue("user_id")
	userID, err := strconv.Atoi(userIDStr)
	if err != nil {
		app.clientError(w, http.StatusBadRequest)
		return
	}

	// Generate UUID for book (used both as DB ID and MinIO filename)
	bookId := uuid.New()

	// Use the UUID as the file name (optionally preserve extension)
	ext := ""
	if parts := strings.Split(header.Filename, "."); len(parts) > 1 {
		ext = "." + parts[len(parts)-1]
	}
	objectName := bookId.String() + ext

	// Upload file to MinIO
	uploadInfo, err := app.minioClient.PutObject(
		context.Background(),
		app.minioBucket,
		objectName,
		file,
		header.Size,
		minio.PutObjectOptions{ContentType: header.Header.Get("Content-Type")},
	)
	if err != nil {
		app.serverError(w, err)
		return
	}

	app.infoLog.Printf("File uploaded to MinIO: %s (%d bytes)", uploadInfo.Key, uploadInfo.Size)

	// Insert into DB using UUID
	// TODO: we'll evaluate the actual book title later with some third party. Maybe the processor should handle that
	bookId, err = app.books.Insert(bookId, header.Filename, header.Filename, objectName, language, userID)
	if err != nil {
		app.serverError(w, err)
		return
	}

	app.infoLog.Printf("Book record inserted: ID=%s, filename=%s", bookId.String(), objectName)

	// --- Enqueue background processing job ---
	enqueueURL := fmt.Sprintf(
		"http://worker-api:8000/enqueue/book?book_id=%s&filename=%s",
		bookId.String(),
		objectName,
	)
	resp, err := http.Post(enqueueURL, "application/json", nil)
	if err != nil {
		app.errorLog.Printf("❌ Failed to enqueue book job: %v", err)
	} else {
		defer resp.Body.Close()
		if resp.StatusCode != http.StatusOK {
			app.errorLog.Printf("⚠️ Enqueue request returned status %d", resp.StatusCode)
		} else {
			app.infoLog.Printf("✅ Book %s successfully enqueued for processing", bookId.String())
		}
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	w.Write([]byte(fmt.Sprintf(`{"status":"uploaded","id":"%s","filename":"%s"}`, bookId.String(), objectName)))
}

func (app *application) getBookWords(w http.ResponseWriter, r *http.Request, bookId uuid.UUID) {
    query := r.URL.Query()

    limit := 50
    offset := 0
    sortOrder := strings.ToLower(query.Get("sort"))
    if sortOrder != "asc" && sortOrder != "desc" {
        sortOrder = "desc"
    }

    difficulty := -1
    if diffStr := query.Get("difficulty"); diffStr != "" {
        if val, err := strconv.Atoi(diffStr); err == nil {
            difficulty = val
        }
    }

    minCount := -1
    if minStr := query.Get("min_count"); minStr != "" {
        if val, err := strconv.Atoi(minStr); err == nil {
            minCount = val
        }
    }

    maxCount := -1
    if maxStr := query.Get("max_count"); maxStr != "" {
        if val, err := strconv.Atoi(maxStr); err == nil {
            maxCount = val
        }
    }

    if lStr := query.Get("limit"); lStr != "" {
        if val, err := strconv.Atoi(lStr); err == nil && val > 0 {
            limit = val
        }
    }
    if oStr := query.Get("offset"); oStr != "" {
        if val, err := strconv.Atoi(oStr); err == nil && val >= 0 {
            offset = val
        }
    }

    words, err := app.bookWords.GetBookWords(bookId, difficulty, minCount, maxCount, limit, offset, sortOrder)
    if err != nil {
        app.serverError(w, err)
        return
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(words)
}
