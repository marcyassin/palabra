package models

import (
    "errors"
    "time"
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
    Processed time.Time // when NLP analysis completed
}