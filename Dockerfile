FROM golang:1.21

WORKDIR /app
COPY . .

RUN go mod tidy

# ⚠️ Keep debug symbols for better CBOM visibility
RUN go build -gcflags="all=-N -l" -o app

CMD ["./app"]
