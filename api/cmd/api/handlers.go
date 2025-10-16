package main

import (
	"context"
	"encoding/json"
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

func (app *application) bookOverview(w http.ResponseWriter, r *http.Request, bookID int) {
	// TODO: Fetch book info and word stats from DB
	overview := map[string]interface{}{
		"book_id":      bookID,
		"title":        "El Problema de los Tres Cuerpos",
		"total_words":  120000,
		"unique_words": 14043,
		"language":     "es",
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(overview)
}

func (app *application) topWords(w http.ResponseWriter, r *http.Request, bookID int) {
	nStr := r.URL.Query().Get("n")
	sortOrder := r.URL.Query().Get("sort")
	if nStr == "" {
		nStr = "50"
	}
	if sortOrder == "" {
		sortOrder = "desc"
	}
	// n, _ := strconv.Atoi(nStr)

	// TODO: Query DB for top N words, ordered by count asc/desc
	words := []map[string]interface{}{
		{"word": "trilogía", "count": 120, "difficulty": 3},
		{"word": "cultura", "count": 98, "difficulty": 2},
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(words)
}

func (app *application) wordsByDifficulty(w http.ResponseWriter, r *http.Request, bookID int) {
	// TODO: Query DB and group words by difficulty
	response := map[string][]map[string]interface{}{
		"1": {{"word": "hola", "count": 23}},
		"2": {{"word": "cultura", "count": 12}},
		"3": {{"word": "trilogía", "count": 5}},
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func (app *application) translateWord(w http.ResponseWriter, r *http.Request) {
	word := r.URL.Query().Get("word")
	lang := r.URL.Query().Get("lang")

	if word == "" || lang == "" {
		app.clientError(w, http.StatusBadRequest)
		return
	}

	// TODO: Query DB or external service for translation
	translation := map[string]interface{}{
		"word":        word,
		"translation": "trilogy", // placeholder
		"language":    lang,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(translation)
}

func (app *application) filteredWords(w http.ResponseWriter, r *http.Request, bookID int) {
	// query := r.URL.Query()
	// difficultyStr := query.Get("difficulty")
	// minCountStr := query.Get("min_count")
	// maxCountStr := query.Get("max_count")

	// TODO: Query DB with filters
	response := []map[string]interface{}{
		{"word": "hola", "count": 23, "difficulty": 1},
		{"word": "cultura", "count": 12, "difficulty": 2},
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}
