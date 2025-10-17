package models

import (
    "errors"
    "time"
)

var ErrNoRecord = errors.New("models: no matching record found")

type Book struct {
    ID        int           `json:"id"`
    Title     string        `json:"title"`
    Filename  string        `json:"filename"`
    Language  string        `json:"language"`
    UserID    int           `json:"userId"`
    Status    string        `json:"status"`
    Created   time.Time     `json:"created"`
    Processed *time.Time  `json:"processed"`
}

type Word struct {
    ID              int       `json:"id"`
    Word            string    `json:"word"`
    Language        string    `json:"language"`
    Difficulty      *int       `json:"difficulty"`
    Translation     *string    `json:"translation"`
    DefinitionEN    *string    `json:"definition_en"`
    DefinitionLocal *string    `json:"definition_local"`
    Created         time.Time `json:"created"`
}

type BookWord struct {
    BookID int 
    WordID int
    Count  int
}

type WordInfo struct {
    Word
    Count int `json:"count"`
}

