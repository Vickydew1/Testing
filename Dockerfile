FROM golang:1.21

WORKDIR /app

# Copy source
COPY . .

# Install dependencies
RUN go mod tidy

# Build binary (keep symbols for better analysis)
RUN go build -gcflags="all=-N -l" -o app

# 🔥 Add real crypto artifacts so CBOM image scan detects something
RUN mkdir /certs && \
    openssl req -x509 -newkey rsa:2048 \
    -keyout /certs/key.pem \
    -out /certs/cert.pem \
    -days 1 -nodes \
    -subj "/CN=cbom-test"

# Optional: show files (debug)
RUN ls -R /certs

CMD ["./app"]
