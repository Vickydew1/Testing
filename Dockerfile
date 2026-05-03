# Build stage
FROM golang:1.21 AS builder

WORKDIR /app
COPY . .

RUN go mod tidy
RUN go build -o app

# Runtime stage
FROM debian:bookworm-slim

WORKDIR /app
COPY --from=builder /app/app .

CMD ["./app"]
