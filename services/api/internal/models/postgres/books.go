package postgres

import (
    "database/sql"
    "github.com/google/uuid"
    "marcyassin/palabra/internal/models"
)

type BookModel struct {
    DB *sql.DB
}

func (m *BookModel) Insert(bookId uuid.UUID, title, filename, originalFilename, language string, userID int) (uuid.UUID, error) {
    query := `
        INSERT INTO books (id, title, filename, original_filename, language, user_id, status, created)
        VALUES ($1, $2, $3, $4, $5, $6, 'pending', NOW())`

    _, err := m.DB.Exec(query, bookId, title, filename, originalFilename, language, userID)
    if err != nil {
        return uuid.Nil, err
    }

    return bookId, nil
}

func (m *BookModel) Get(bookId uuid.UUID) (*models.Book, error) {
    query := `
        SELECT id, title, filename, original_filename, language, user_id, status, created, processed
        FROM books
        WHERE id = $1`

    b := &models.Book{}
    err := m.DB.QueryRow(query, bookId).Scan(
        &b.ID, &b.Title, &b.Filename, &b.OriginalFilename,
        &b.Language, &b.UserID, &b.Status, &b.Created, &b.Processed,
    )

    if err != nil {
        if err == sql.ErrNoRows {
            return nil, models.ErrNoRecord
        }
        return nil, err
    }

    return b, nil
}

func (m *BookModel) Latest(limit int) ([]*models.Book, error) {
    query := `
        SELECT id, title, filename, original_filename, language, user_id, status, created, processed
        FROM books
        ORDER BY created DESC
        LIMIT $1`

    rows, err := m.DB.Query(query, limit)
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var books []*models.Book
    for rows.Next() {
        b := &models.Book{}
        err = rows.Scan(
            &b.ID, &b.Title, &b.Filename, &b.OriginalFilename,
            &b.Language, &b.UserID, &b.Status, &b.Created, &b.Processed,
        )
        if err != nil {
            return nil, err
        }
        books = append(books, b)
    }

    if err = rows.Err(); err != nil {
        return nil, err
    }

    return books, nil
}
