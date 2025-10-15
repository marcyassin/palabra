package main

import (
    "database/sql"
    "flag"
    "log"
    "net/http"
    "os"

    "marcyassin/bookprep/internal/models/postgres"

    _ "github.com/lib/pq"
)

type application struct {
    errorLog *log.Logger
    infoLog  *log.Logger
    db       *sql.DB
    books    *postgres.BookModel
}

func main() {
    addr := flag.String("addr", ":4000", "HTTP network address")
    dsn := flag.String("dsn", "postgres://bookprep_user:secret@localhost:5432/bookprep?sslmode=disable", "Postgres data source name")
    flag.Parse()

    infoLog := log.New(os.Stdout, "INFO\t", log.Ldate|log.Ltime)
    errorLog := log.New(os.Stderr, "ERROR\t", log.Ldate|log.Ltime|log.Lshortfile)

    db, err := openDB(*dsn)
    if err != nil {
        errorLog.Fatal(err)
    }
    defer db.Close()

    app := &application{
        errorLog: errorLog,
        infoLog:  infoLog,
        db:       db,
        books: &postgres.BookModel{DB: db},
    }

    srv := &http.Server{
        Addr:     *addr,
        ErrorLog: errorLog,
        Handler:  app.routes(),
    }

    infoLog.Printf("Starting server on %s", *addr)
    err = srv.ListenAndServe()
    errorLog.Fatal(err)
}

func openDB(dsn string) (*sql.DB, error) {
    db, err := sql.Open("postgres", dsn)
    if err != nil {
        return nil, err
    }
    if err = db.Ping(); err != nil {
        return nil, err
    }
    return db, nil
}
    