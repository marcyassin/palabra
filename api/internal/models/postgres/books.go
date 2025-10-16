package postgres

import (
    "database/sql"

    "marcyassin/palabra/internal/models"
)

type BookModel struct {
    DB *sql.DB
}

func (m *BookModel) Insert(title, filename, language string, userID int) (int, error) {
    query := `
        INSERT INTO books (title, filename, language, user_id, status, created)
        VALUES ($1, $2, $3, $4, 'pending', NOW())
        RETURNING id`
    
    var id int
    err := m.DB.QueryRow(query, title, filename, language, userID).Scan(&id)
    if err != nil {
        return 0, err
    }
    return id, nil
}

func (m *BookModel) Get(id int) (*models.Book, error) {
    query := `
        SELECT id, title, filename, language, user_id, status, created, processed
        FROM books
        WHERE id = $1`
    
    b := &models.Book{}
    err := m.DB.QueryRow(query, id).Scan(
        &b.ID, &b.Title, &b.Filename, &b.Language, &b.UserID,
        &b.Status, &b.Created, &b.Processed,
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
    if limit <= 0 {
        limit = 10
    }

    query := `
        SELECT id, title, filename, language, user_id, status, created, processed
        FROM books
        ORDER BY created DESC
        LIMIT $1`
    
    rows, err := m.DB.Query(query, limit)
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    books := []*models.Book{}
    for rows.Next() {
        b := &models.Book{}
        if err := rows.Scan(&b.ID, &b.Title, &b.Filename, &b.Language, &b.UserID,
            &b.Status, &b.Created, &b.Processed); err != nil {
            return nil, err
        }
        books = append(books, b)
    }
    if err = rows.Err(); err != nil {
        return nil, err
    }
    return books, nil
}
