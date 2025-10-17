package main

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"sort"
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

func (app *application) getBook(w http.ResponseWriter, r *http.Request, bookId int) {
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

	uniqueFilename := uuid.New().String() + "-" + header.Filename

	uploadInfo, err := app.minioClient.PutObject(
		context.Background(),
		app.minioBucket,
		uniqueFilename,
		file,
		header.Size,
		minio.PutObjectOptions{ContentType: header.Header.Get("Content-Type")},
	)
	if err != nil {
		app.serverError(w, err)
		return
	}

	app.infoLog.Printf("File uploaded to MinIO: %s (%d bytes)", uploadInfo.Key, uploadInfo.Size)

	bookId, err := app.books.Insert(header.Filename, uniqueFilename, language, userID)
	if err != nil {
		app.serverError(w, err)
		return
	}

	app.infoLog.Printf("Book record inserted: ID=%d, filename=%s", bookId, uniqueFilename)

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	w.Write([]byte(fmt.Sprintf(`{"status":"uploaded","id":%d,"filename":"%s"}`, bookId, uniqueFilename)))
}

func (app *application) getBookWords(w http.ResponseWriter, r *http.Request, bookID int) {
    query := r.URL.Query()

    // Params
    nStr := query.Get("n")
    sortOrder := strings.ToLower(query.Get("sort"))
    difficultyStr := query.Get("difficulty")
    minCountStr := query.Get("min_count")
    maxCountStr := query.Get("max_count")

    // Defaults
    n := 1000
    if nStr != "" {
        if val, err := strconv.Atoi(nStr); err == nil && val > 0 {
            n = val
        }
    }

    if sortOrder != "asc" && sortOrder != "desc" {
        sortOrder = "desc"
    }

    // Optional filters
    difficulty := -1
    if difficultyStr != "" {
        if val, err := strconv.Atoi(difficultyStr); err == nil {
            difficulty = val
        }
    }
    minCount := -1
    if minCountStr != "" {
        if val, err := strconv.Atoi(minCountStr); err == nil {
            minCount = val
        }
    }
    maxCount := -1
    if maxCountStr != "" {
        if val, err := strconv.Atoi(maxCountStr); err == nil {
            maxCount = val
        }
    }

    // Step 1: Fetch word counts for book
    wordCounts, err := app.bookWords.GetByBook(bookID)
    if err != nil {
        app.serverError(w, err)
        return
    }
    if len(wordCounts) == 0 {
        w.Header().Set("Content-Type", "application/json")
        json.NewEncoder(w).Encode([]interface{}{})
        return
    }

    // Step 2: Load word details
    wordIDs := make([]int, 0, len(wordCounts))
    for id := range wordCounts {
        wordIDs = append(wordIDs, id)
    }

    placeholders := make([]string, len(wordIDs))
    args := make([]interface{}, len(wordIDs))
    for i, id := range wordIDs {
        placeholders[i] = fmt.Sprintf("$%d", i+1)
        args[i] = id
    }

    queryStr := fmt.Sprintf(`
        SELECT id, word, COALESCE(difficulty, 0) AS difficulty
        FROM words
        WHERE id IN (%s)
    `, strings.Join(placeholders, ","))

    rows, err := app.db.Query(queryStr, args...)
    if err != nil {
        app.serverError(w, err)
        return
    }
    defer rows.Close()

    type wordInfo struct {
        Word       string `json:"word"`
        Count      int    `json:"count"`
        Difficulty int    `json:"difficulty"`
    }

    words := []wordInfo{}
    for rows.Next() {
        var id, diff int
        var wText string
        if err := rows.Scan(&id, &wText, &diff); err != nil {
            app.serverError(w, err)
            return
        }

        count := wordCounts[id]

        // Apply filters
        if difficulty != -1 && diff != difficulty {
            continue
        }
        if minCount != -1 && count < minCount {
            continue
        }
        if maxCount != -1 && count > maxCount {
            continue
        }

        words = append(words, wordInfo{
            Word:       wText,
            Count:      count,
            Difficulty: diff,
        })
    }

    // Step 3: Sort
    sort.Slice(words, func(i, j int) bool {
        if sortOrder == "asc" {
            return words[i].Count < words[j].Count
        }
        return words[i].Count > words[j].Count
    })

    // Step 4: Limit
    if len(words) > n {
        words = words[:n]
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(words)
}

