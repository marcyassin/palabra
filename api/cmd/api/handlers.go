package main

import (
	"context" 
    "fmt"
    "net/http"
	"strconv"
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

func (app *application) listBooks(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		w.Header().Set("Allow", http.MethodGet)
		app.clientError(w, http.StatusMethodNotAllowed)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	w.Write([]byte(`{"books": []}`))
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

    bookID, err := app.books.Insert(header.Filename, uniqueFilename, language, userID)
    if err != nil {
        app.serverError(w, err)
        return
    }

    app.infoLog.Printf("Book record inserted: ID=%d, filename=%s", bookID, uniqueFilename)

    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(http.StatusCreated)
    w.Write([]byte(fmt.Sprintf(`{"status":"uploaded","id":%d,"filename":"%s"}`, bookID, uniqueFilename)))
}