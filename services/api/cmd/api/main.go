package main

import (
    "context"
    "database/sql"
    "fmt"
    "log"
    "net/http"
    "os"
    "strconv"

    "github.com/joho/godotenv"
    "github.com/minio/minio-go/v7"
    "github.com/minio/minio-go/v7/pkg/credentials"
    _ "github.com/lib/pq"

    "marcyassin/palabra/internal/models/postgres"
)

type application struct {
    errorLog    *log.Logger
    infoLog     *log.Logger
    db          *sql.DB
    books       *postgres.BookModel
    bookWords   *postgres.BookWordsModel
    minioClient *minio.Client
    minioBucket string
}

func main() {
    infoLog := log.New(os.Stdout, "INFO\t", log.Ldate|log.Ltime)
    errorLog := log.New(os.Stderr, "ERROR\t", log.Ldate|log.Ltime|log.Lshortfile)

    if err := godotenv.Load(); err != nil {
        errorLog.Println("No .env file found — continuing with environment variables")
    }

    addr := getEnv("APP_ADDR", ":4000")
    dsn := getEnv("DATABASE_URL", "postgresql://palabra:secret@localhost:5432/palabra?sslmode=disable")
    if dsn == "" {
        errorLog.Fatal("DATABASE_URL must be set")
    }

    minioEndpoint := getEnv("MINIO_ENDPOINT", "localhost:9000")
    minioAccess := getEnv("MINIO_ACCESS_KEY", "minioadmin")
    minioSecret := getEnv("MINIO_SECRET_KEY", "minioadmin")
    minioUseSSL := getEnv("MINIO_SSL", "false")
    minioBucket := getEnv("MINIO_BUCKET", "palabra")

    useSSL, _ := strconv.ParseBool(minioUseSSL)

    db, err := openDB(dsn)
    if err != nil {
        errorLog.Fatalf("Database connection failed: %v", err)
    }
    defer db.Close()

    minioClient, err := openMinIO(minioEndpoint, minioAccess, minioSecret, useSSL)
    if err != nil {
    errorLog.Fatalf("MinIO connection failed: %v", err)
    }
    ensureBucket(minioClient, minioBucket, infoLog, errorLog)

    app := &application{
        errorLog:    errorLog,
        infoLog:     infoLog,
        db:          db,
        books:       &postgres.BookModel{DB: db},
        bookWords:   &postgres.BookWordsModel{DB: db},
        minioClient: minioClient,
        minioBucket: minioBucket,
    }

    srv := &http.Server{
        Addr:     addr,
        ErrorLog: errorLog,
        Handler:  app.routes(),
    }

    infoLog.Printf("Starting server on %s", addr)
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

func openMinIO(endpoint, accessKey, secretKey string, useSSL bool) (*minio.Client, error) {
    client, err := minio.New(endpoint, &minio.Options{
        Creds:  credentials.NewStaticV4(accessKey, secretKey, ""),
        Secure: useSSL,
    })
    if err != nil {
        return nil, fmt.Errorf("failed to initialize MinIO client: %w", err)
    }

    if _, err := client.ListBuckets(context.Background()); err != nil {
        return nil, fmt.Errorf("failed to connect to MinIO: %w", err)
    }

    return client, nil
}

func ensureBucket(client *minio.Client, bucketName string, infoLog *log.Logger, errorLog *log.Logger) {
    ctx := context.Background()

    exists, err := client.BucketExists(ctx, bucketName)
    if err != nil {
        errorLog.Fatalf("Failed to check if bucket exists: %v", err)
    }

    if !exists {
        if err := client.MakeBucket(ctx, bucketName, minio.MakeBucketOptions{}); err != nil {
            errorLog.Fatalf("Failed to create bucket %s: %v", bucketName, err)
        }
        infoLog.Printf("Created bucket: %s", bucketName)
    } else {
        infoLog.Printf("Bucket %s already exists", bucketName)
    }
}

func getEnv(key, fallback string) string {
    if value, exists := os.LookupEnv(key); exists {
        return value
    }
    return fallback
}
