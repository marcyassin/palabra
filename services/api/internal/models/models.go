package models

import (
    "errors"
    "time"
    "github.com/google/uuid"
)

var ErrNoRecord = errors.New("models: no matching record found")

type Book struct {
    ID               uuid.UUID  `json:"id"`
    Title            string     `json:"title"`
    Filename         string     `json:"filename"`
    OriginalFilename string     `json:"original_filename"`
    Language         string     `json:"language"`
    UserID           int        `json:"userId"`
    Status           string     `json:"status"`
    Created          time.Time  `json:"created"`
    Processed        *time.Time `json:"processed"`
}

type Word struct {
    ID         int        `json:"id"`
    Word       string     `json:"word"`
    Language   string     `json:"language"`
    Difficulty *int       `json:"difficulty,omitempty"`
    ZipfScore  *float64   `json:"zipfScore,omitempty"`
    Created    time.Time  `json:"created"`
}

type BookWord struct {
    BookID int `json:"bookId"`
    WordID int `json:"wordId"`
    Count  int `json:"count"`
}

type WordInfo struct {
    Word
    Count int `json:"count"`
}
