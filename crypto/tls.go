package crypto

import (
	"crypto/tls"
	"fmt"
)

func UseTLS() {
	config := &tls.Config{
		MinVersion: tls.VersionTLS12,
	}
	fmt.Println("TLS minimum version:", config.MinVersion)
}
