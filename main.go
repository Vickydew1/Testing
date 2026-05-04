package main

import (
	"fmt"

	"cbom-test/crypto"
)

func main() {
	fmt.Println("CBOM Test App")

	crypto.HashData("hello-accuknox")
	crypto.UseTLS()
	crypto.GenerateRSA()
}
