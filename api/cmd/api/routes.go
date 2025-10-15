package main

import "net/http"

func (app *application) routes() *http.ServeMux {
	mux := http.NewServeMux()

	mux.HandleFunc("/", app.home)
	mux.HandleFunc("/api", app.apiRoot)
	mux.HandleFunc("/api/books", app.listBooks)
	mux.HandleFunc("/api/books/upload", app.uploadBook)

	return mux
}
