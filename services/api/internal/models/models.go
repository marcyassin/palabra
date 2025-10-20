package models

import (
    "errors"
    "time"
)

var ErrNoRecord = errors.New("models: no matching record found")

type Book struct {
    ID        int        `json:"id"`
    Title     string     `json:"title"`
    Filename  string     `json:"filename"`
    Language  string     `json:"language"`
    UserID    *int       `json:"userId,omitempty"`
    Status    string     `json:"status"`
    Created   time.Time  `json:"created"`
    Processed *time.Time `json:"processed,omitempty"`
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
