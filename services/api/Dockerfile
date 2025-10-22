FROM golang:1.25-alpine

WORKDIR /app

RUN apk add --no-cache git bash

COPY go.mod go.sum ./
RUN go mod download

COPY . .

EXPOSE 4000

# Default command (Compose will override if you use `go run ./cmd/api`)
CMD ["go", "run", "./cmd/api"]
