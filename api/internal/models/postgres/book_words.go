package postgres

import (
    "database/sql"
    "fmt"
    "strings"

    "marcyassin/palabra/internal/models"
)

type BookWordsModel struct {
    DB *sql.DB
}

func (m *BookWordsModel) Insert(bookID, wordID, count int) error {
    query := `
        INSERT INTO book_words (book_id, word_id, count)
        VALUES ($1, $2, $3)
        ON CONFLICT (book_id, word_id)
        DO UPDATE SET count = book_words.count + EXCLUDED.count;
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

func (m *BookWordsModel) GetBookWords(
    bookID int,
    difficulty, minCount, maxCount, limit, offset int,
    sortOrder string,
) ([]models.WordInfo, error) {
    args := []interface{}{bookID}
    whereClauses := []string{"bw.book_id = $1"}

    if difficulty != -1 {
        args = append(args, difficulty)
        whereClauses = append(whereClauses, fmt.Sprintf("w.difficulty = $%d", len(args)))
    }
    if minCount != -1 {
        args = append(args, minCount)
        whereClauses = append(whereClauses, fmt.Sprintf("bw.count >= $%d", len(args)))
    }
    if maxCount != -1 {
        args = append(args, maxCount)
        whereClauses = append(whereClauses, fmt.Sprintf("bw.count <= $%d", len(args)))
    }

    // Append limit and offset
    args = append(args, limit, offset)

    // Safe ordering fallback
    if sortOrder != "ASC" && sortOrder != "DESC" {
        sortOrder = "DESC"
    }

    queryStr := fmt.Sprintf(`
        SELECT w.id, w.word, w.language, w.difficulty, w.zipf_score, w.created, bw.count
        FROM book_words bw
        JOIN words w ON w.id = bw.word_id
        WHERE %s
        ORDER BY bw.count %s
        LIMIT $%d OFFSET $%d;
    `, strings.Join(whereClauses, " AND "), sortOrder, len(args)-1, len(args))

    rows, err := m.DB.Query(queryStr, args...)
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    words := []models.WordInfo{}
    for rows.Next() {
        var w models.WordInfo
        if err := rows.Scan(
            &w.Word.ID,
            &w.Word.Word,
            &w.Word.Language,
            &w.Word.Difficulty,
            &w.Word.ZipfScore,
            &w.Word.Created,
            &w.Count,
        ); err != nil {
            return nil, err
        }
        words = append(words, w)
    }

    if err = rows.Err(); err != nil {
        return nil, err
    }

    return words, nil
}
