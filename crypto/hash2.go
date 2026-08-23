package crypto

import (
	"crypto/sha256"
	"fmt"
)

func HashData(input string) {
	hash := sha256.Sum256([]byte(input))
	fmt.Printf("SHA256: %x\n", hash)
}
