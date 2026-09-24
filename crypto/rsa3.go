package crypto

import (
	"crypto/rand"
	"crypto/rsa"
	"fmt"
)

func GenerateRSA() {
	key, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		fmt.Println("Error generating RSA key:", err)
		return
	}
	fmt.Println("RSA key size:", key.Size())
}
