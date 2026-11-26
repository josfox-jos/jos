// Example 04: Zero-Dependency Go Service / MCP Verification Middleware (josfox.cloud/jos@v0.1.2).
// Run: go run 04_go_mcp_gateway.go
package main

import (
	"fmt"
	"josfox.cloud/jos"
)

func main() {
	envelope := map[string]any{
		"jos":       map[string]any{"version": "2.5.0", "kind": "atom"},
		"meta":      map[string]any{"name": "mcp-search-services", "version": "0.1.0"},
		"intention": map[string]any{"objective": "discover_local_foxtails|cap=registry:read"},
	}
	sealedBytes, artID, err := jos.Seal(envelope)
	if err != nil {
		panic(err)
	}
	verifiedArt, err := jos.Verify(sealedBytes)
	if err != nil {
		panic(err)
	}
	fmt.Printf("[GO GATEWAY] Sealed & Verified: %s (match=%v)\n", verifiedArt, artID == verifiedArt)
}
