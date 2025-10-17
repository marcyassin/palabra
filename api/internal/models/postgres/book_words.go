package postgres

import (
    "database/sql"
)

type BookWordsModel struct {
    DB *sql.DB
}

func (m *BookWordsModel) Insert(bookID, wordID, count int) error {
    query := `
        INSERT INTO book_words (book_id, word_id, count)
        VALUES ($1, $2, $3)
        ON CONFLICT (book_id, word_id) DO UPDATE
        SET count = book_words.count + EXCLUDED.count
    `
    _, err := m.DB.Exec(query, bookID, wordID, count)
    return err
}

func (m *BookWordsModel) GetByBook(bookID int) (map[int]int, error) {
    query := `SELECT word_id, count FROM book_words WHERE book_id = $1`
    rows, err := m.DB.Query(query, bookID)
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    result := make(map[int]int)
    for rows.Next() {
        var wordID, count int
        if err := rows.Scan(&wordID, &count); err != nil {
            return nil, err
        }
        result[wordID] = count
    }
    if err = rows.Err(); err != nil {
        return nil, err
    }
    return result, nil
}
