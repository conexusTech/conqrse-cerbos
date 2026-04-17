.PHONY: help test test-js test-bash test-watch test-verbose test-ci results clean

# Configuration
CERBOS_URL ?= http://localhost:3592
OUTPUT_DIR ?= ./test-results

# Default target
help:
	@echo "Cerbos Policy Test Suite"
	@echo ""
	@echo "Usage:"
	@echo "  make test              Run tests (Node.js runner)"
	@echo "  make test-js           Run tests with Node.js"
	@echo "  make test-bash         Run tests with Bash"
	@echo "  make test-watch        Run tests in watch mode"
	@echo "  make test-verbose      Run tests with verbose output"
	@echo "  make test-ci           Run tests for CI/CD (exits with code)"
	@echo "  make results           Show test results"
	@echo "  make clean             Clean test results"
	@echo ""
	@echo "Environment Variables:"
	@echo "  CERBOS_URL=<url>       Cerbos server URL (default: $(CERBOS_URL))"
	@echo "  OUTPUT_DIR=<dir>       Output directory (default: $(OUTPUT_DIR))"
	@echo ""
	@echo "Examples:"
	@echo "  make test"
	@echo "  CERBOS_URL=http://cerbos.example.com:3592 make test"
	@echo "  make test-watch"

# Run tests with Node.js (default)
test: test-js

# Run tests with Node.js
test-js:
	@echo "Running Cerbos policy tests (Node.js)..."
	@CERBOS_URL=$(CERBOS_URL) OUTPUT_DIR=$(OUTPUT_DIR) node tests/run-tests.js

# Run tests with Bash
test-bash:
	@echo "Running Cerbos policy tests (Bash)..."
	@CERBOS_URL=$(CERBOS_URL) OUTPUT_DIR=$(OUTPUT_DIR) bash tests/run-tests.sh

# Run tests in watch mode (requires nodemon)
test-watch:
	@echo "Running Cerbos policy tests in watch mode..."
	@if command -v nodemon &> /dev/null; then \
		CERBOS_URL=$(CERBOS_URL) OUTPUT_DIR=$(OUTPUT_DIR) nodemon --watch tests --watch policies -e js,json,yaml tests/run-tests.js; \
	else \
		echo "nodemon not installed. Install with: npm install -g nodemon"; \
		exit 1; \
	fi

# Run tests with verbose output
test-verbose:
	@echo "Running Cerbos policy tests (verbose)..."
	@CERBOS_URL=$(CERBOS_URL) OUTPUT_DIR=$(OUTPUT_DIR) DEBUG=* node tests/run-tests.js

# Run tests for CI/CD pipeline
test-ci: test-js
	@if [ -f "$(OUTPUT_DIR)/results.json" ]; then \
		echo ""; \
		echo "Test results summary:"; \
		jq '.summary' $(OUTPUT_DIR)/results.json; \
	fi

# Show test results
results:
	@if [ -f "$(OUTPUT_DIR)/results.json" ]; then \
		jq . $(OUTPUT_DIR)/results.json | head -50; \
		echo ""; \
		echo "Full results: $(OUTPUT_DIR)/results.json"; \
	else \
		echo "No test results found. Run 'make test' first."; \
		exit 1; \
	fi

# Clean test results
clean:
	@echo "Cleaning test results..."
	@rm -rf $(OUTPUT_DIR)
	@echo "Cleaned: $(OUTPUT_DIR)"

# Health check
health:
	@echo "Checking Cerbos server: $(CERBOS_URL)"
	@curl -s -m 5 $(CERBOS_URL)/health > /dev/null && echo "✓ Cerbos is healthy" || echo "✗ Cerbos is not responding"

# List test cases
list-tests:
	@echo "Available test cases:"
	@jq -r '.testSuites[] | .name' tests/test-cases.json
	@echo ""
	@jq -r '.testSuites[].tests[] | "  \(.id): \(.name)"' tests/test-cases.json
