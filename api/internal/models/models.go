package models

import (
    "errors"
    "time"
    "database/sql"
)

var ErrNoRecord = errors.New("models: no matching record found")

type Book struct {
    ID        int       // primary key
    Title     string    // book title
    Filename  string    // name of uploaded file in MinIO
    Language  string    // e.g., "es" for Spanish
    UserID    int       // if multiple users will upload books
    Status    string    // "pending", "processing", "done"
    Created   time.Time
    Processed sql.NullTime // when NLP analysis completed
}

type Word struct {
    ID         int
    Word       string    // the word itself
    Language   string    // language code, e.g., "es"
    Difficulty int       // 1–6 for now, corresponding to A1–C2
    Frequency  int       // total frequency across all books
    Created    time.Time // record created timestamp
}

type BookWord struct {
    BookID int // references Book.ID
    WordID int // references Word.ID
    Count  int // number of times this word occurs in the book
}
