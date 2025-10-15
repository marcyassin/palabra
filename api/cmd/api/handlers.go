package main

import (
    "fmt"
    "net/http"
)

func (app *application) home(w http.ResponseWriter, r *http.Request) {
    if r.URL.Path != "/" {
        app.notFound(w)
        return
    }

    w.Header().Set("Content-Type", "text/plain; charset=utf-8")
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("BookPrep API Service"))
}

func (app *application) apiRoot(w http.ResponseWriter, r *http.Request) {
	if r.URL.Path != "/api" {
		app.notFound(w)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	w.Write([]byte(`{
		"service": "BookPrep API",
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
	userID := r.FormValue("user_id")

	app.infoLog.Printf("Uploaded file: %s (language=%s, user=%s)", header.Filename, language, userID)

	// TODO: Add file upload logic (e.g., MinIO, text extraction, etc.)

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	w.Write([]byte(fmt.Sprintf(`{"status": "uploaded", "filename": "%s"}`, header.Filename)))
}
