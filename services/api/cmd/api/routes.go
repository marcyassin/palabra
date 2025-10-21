package main

import (
	"net/http"

	"github.com/google/uuid"
	"github.com/gorilla/mux"
)

func (app *application) withBookID(h func(http.ResponseWriter, *http.Request, uuid.UUID)) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		vars := mux.Vars(r)
		idStr := vars["id"]

		bookID, err := uuid.Parse(idStr)
		if err != nil {
			http.Error(w, "Invalid Book ID", http.StatusBadRequest)
			return
		}

		h(w, r, bookID)
	}
}

func (app *application) routes() *mux.Router {
	r := mux.NewRouter()

	r.HandleFunc("/", app.home)
	r.HandleFunc("/api", app.apiRoot)

	r.HandleFunc("/api/books", app.getBooks).Methods("GET")
	r.HandleFunc("/api/books/upload", app.uploadBook).Methods("POST")

	// UUID pattern: 8-4-4-4-12 hex characters
	r.HandleFunc("/api/books/{id:[0-9a-fA-F\\-]{36}}", app.withBookID(app.getBook)).Methods("GET")
	r.HandleFunc("/api/books/{id:[0-9a-fA-F\\-]{36}}/words", app.withBookID(app.getBookWords)).Methods("GET")

	return r
}
