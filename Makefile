.PHONY: help gate okf-check generate-check build-types generate-types generate-policies generate-tests policy-tests test test-js test-bash test-watch test-verbose test-ci results clean

# Configuration
CERBOS_URL ?= http://localhost:3592
OUTPUT_DIR ?= ./test-results

# Default target
help:
	@echo "Cerbos Policy Test Suite"
	@echo ""
	@echo "Usage:"
	@echo "  make gate              Run the local process-v3 completion gate"
	@echo "  make okf-check         Validate the OKF knowledge bundle"
	@echo "  make generate-check    Parse the matrix and preview generated output"
	@echo "  make build-types       Build the permission-types package"
	@echo "  make generate-types    Generate TypeScript enums from matrix"
	@echo "  make generate-policies Generate Cerbos policies from matrix"
	@echo "  make test              Run native Cerbos policy decision tests"
	@echo "  make test-js           Compatibility alias for native policy tests"
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

# Process-v3 local gate. Live Cerbos and cluster checks remain explicit because
# they require external services and deployment authorization.
gate: okf-check generate-check build-types policy-tests

okf-check:
	@node scripts/okf-check.mjs

generate-check:
	@python3 scripts/generate_policies.py --dry-run
	@python3 scripts/generate_types.py --dry-run
	@python3 scripts/generate_policy_tests.py --check

build-types:
	@npm --prefix packages/permission-types run build

# Generate TypeScript enums and types from resource matrix
generate-types:
	@echo "Generating TypeScript enums and types..."
	@python3 scripts/generate_types.py

# Generate Cerbos policies from resource matrix
generate-policies:
	@echo "Generating Cerbos policy files..."
	@python3 scripts/generate_policies.py

# Generate native Cerbos compile tests from the maintained JSON cases.
generate-tests:
	@python3 scripts/generate_policy_tests.py

# Evaluate checked-in policies and all native test cases in an ephemeral PDP image.
policy-tests:
	@docker run --rm -v "$(CURDIR)/k8s/base/policies:/policies:ro" ghcr.io/cerbos/cerbos:0.51.0 compile /policies

test: policy-tests

test-js: policy-tests

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
