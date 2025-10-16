package main

import (
	"net/http"
	"strconv"

	"github.com/gorilla/mux"
)

func (app *application) withBookID(h func(http.ResponseWriter, *http.Request, int)) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		vars := mux.Vars(r)
		bookID, err := strconv.Atoi(vars["id"])
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

	r.HandleFunc("/api/books/{id:[0-9]+}", app.withBookID(app.getBook)).Methods("GET")
	r.HandleFunc("/api/books/{id:[0-9]+}/top-words", app.withBookID(app.topWords)).Methods("GET")
	r.HandleFunc("/api/books/{id:[0-9]+}/words-by-difficulty", app.withBookID(app.wordsByDifficulty)).Methods("GET")
	r.HandleFunc("/api/books/{id:[0-9]+}/filtered-words", app.withBookID(app.filteredWords)).Methods("GET")

	return r
}
