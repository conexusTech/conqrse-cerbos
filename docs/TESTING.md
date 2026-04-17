# Cerbos Policy Testing Guide

Complete guide for testing the Conqrse Cerbos authorization policies.

## Quick Start

### 1. Start Cerbos Server

```bash
# Using Docker
docker run -it -p 3592:3592 ghcr.io/cerbos/cerbos:latest /cerbos run --log-level=info

# Or your Kubernetes deployment
kubectl port-forward svc/cerbos 3592:3592
```

### 2. Run Tests

```bash
# Default (Node.js runner)
make test

# Or directly
node tests/run-tests.js

# Or with Bash
bash tests/run-tests.sh
```

### 3. View Results

```bash
make results
```

## Test Suite Overview

**18 test scenarios** covering:
- All user levels: SU (Super User), Agency, Retailer
- All user types: Owner, Admin, Lead, Member, Collaborator
- Direct access patterns
- "Act AS" delegation patterns
- Product subscription validation
- Settings access restrictions

### Allow Scenarios (10)

Tests that validate correct access is granted:

1. **allow_1** — Retailer Member listing QR campaigns (direct)
2. **allow_2** — SU Admin acting AS Retailer Admin creating user (delegation)
3. **allow_3** — Agency Admin acting AS Retailer creating campaign (delegation)
4. **allow_4** — Agency Owner creating user for child retailer (direct)
5. **allow_5** — SU Owner managing system settings (direct)
6. **allow_6** — SU Lead viewing system data (read access)
7. **allow_7** — SU Collaborator acting AS Retailer member (delegated read-only)
8. **allow_8** — Agency Lead acting AS Retailer creating resources (delegation)
9. **allow_9** — Agency Member viewing child retailer resources (direct)
10. **allow_10** — Retailer Owner managing store settings (direct)

### Deny Scenarios (8)

Tests that validate incorrect access is denied:

1. **deny_1** — Retailer Collaborator trying to create (read-only)
2. **deny_2** — Retailer Member accessing unsubscribed product (product validation)
3. **deny_3** — SU Collaborator trying to create settings (no settings)
4. **deny_4** — Agency Lead trying to modify settings (no settings)
5. **deny_5** — Agency Collaborator trying to create (read-only)
6. **deny_6** — Retailer Lead trying to modify settings (no settings)
7. **deny_7** — Agency user acting AS unrelated retailer (not child)
8. **deny_8** — Retailer user trying to act AS another retailer (cannot delegate)

## Running Tests

### Using Make

```bash
# Run all tests
make test

# Run with specific Cerbos URL
CERBOS_URL=http://cerbos.example.com:3592 make test

# Run in watch mode (auto-rerun on changes)
make test-watch

# Show test results
make results

# Clean results
make clean

# Health check
make health

# List all tests
make list-tests
```

### Using Node.js Directly

```bash
# Run tests
node tests/run-tests.js

# With custom Cerbos URL
CERBOS_URL=http://cerbos.example.com:3592 node tests/run-tests.js

# With custom output directory
OUTPUT_DIR=./my-results node tests/run-tests.js
```

### Using Bash

```bash
# Run tests
bash tests/run-tests.sh

# With custom Cerbos URL
CERBOS_URL=http://cerbos.example.com:3592 bash tests/run-tests.sh

# With custom output directory
OUTPUT_DIR=./my-results bash tests/run-tests.sh
```

## Test Results

Results are saved to `test-results/results.json`:

```bash
# View summary
jq '.summary' test-results/results.json

# View all results
jq '.' test-results/results.json

# View specific suite results
jq '.suites[0]' test-results/results.json

# Check success rate
jq '.summary.successRate' test-results/results.json
```

Example results:
```json
{
  "summary": {
    "totalSuites": 2,
    "totalTests": 18,
    "passed": 18,
    "failed": 0,
    "successRate": 100.0,
    "duration": 2.34
  }
}
```

## Test Configuration

### Environment Variables

```bash
# Cerbos server URL
CERBOS_URL=http://localhost:3592

# Output directory for results
OUTPUT_DIR=./test-results

# Example
CERBOS_URL=https://cerbos.prod.example.com:3592 OUTPUT_DIR=/var/test-results make test
```

### Test Cases File

Test cases are defined in `tests/test-cases.json`:

```json
{
  "testSuites": [
    {
      "name": "Allow Scenarios",
      "description": "Valid access patterns",
      "tests": [
        {
          "id": "allow_1",
          "name": "Test name",
          "description": "Test description",
          "principal": { /* principal attributes */ },
          "resource": { /* resource attributes */ },
          "action": "resource:list",
          "expectedResult": "ALLOW"
        }
      ]
    }
  ]
}
```

## Adding Custom Tests

1. Open `tests/test-cases.json`
2. Add test to appropriate `testSuites` array
3. Follow the structure:

```json
{
  "id": "custom_1",
  "name": "Descriptive test name",
  "description": "What this test validates",
  "principal": {
    "id": "user-123",
    "userLevel": "retailer",
    "userType": "member",
    "products": ["qr"],
    "agencyId": "agency-456",
    "retailerId": "retail-789"
  },
  "resource": {
    "product": "qr",
    "retailerId": "retail-789"
  },
  "action": "resource:view",
  "expectedResult": "ALLOW"
}
```

4. Run tests to validate

## CI/CD Integration

### GitHub Actions

```yaml
name: Test Cerbos Policies

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      cerbos:
        image: ghcr.io/cerbos/cerbos:latest
        ports:
          - 3592:3592
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: node tests/run-tests.js
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-results
          path: test-results/
```

### GitLab CI

```yaml
test_cerbos:
  image: node:18
  services:
    - name: ghcr.io/cerbos/cerbos:latest
      alias: cerbos
  script:
    - node tests/run-tests.js
  variables:
    CERBOS_URL: http://cerbos:3592
  artifacts:
    paths:
      - test-results/
    reports:
      junit: test-results/results.xml
```

### Docker

```dockerfile
FROM node:18
WORKDIR /app
COPY . .

# Run tests against Cerbos
RUN CERBOS_URL=http://cerbos:3592 node tests/run-tests.js

# Or for Kubernetes
# RUN CERBOS_URL=http://cerbos.default.svc.cluster.local:3592 node tests/run-tests.js
```

## Troubleshooting

### Tests Won't Run

```bash
# Check Cerbos is running
make health

# Check Node.js is installed
node --version

# Check test file exists
ls tests/test-cases.json
```

### Connection Errors

```bash
# Test Cerbos connectivity
curl -v http://localhost:3592/health

# Check URL is correct
echo $CERBOS_URL

# Try with explicit URL
CERBOS_URL=http://localhost:3592 node tests/run-tests.js
```

### Test Failures

1. Check Cerbos logs for policy errors
2. Verify policies are loaded: `curl http://localhost:3592/api/policies`
3. Review test case requirements in documentation
4. Check principal/resource attributes are valid
5. Verify derived roles match policy definitions

### Permission Issues

```bash
# Make scripts executable
chmod +x tests/run-tests.js tests/run-tests.sh

# Check output directory is writable
touch test-results/.write-test && rm test-results/.write-test
```

## Development Workflow

### Watch Mode

Automatically re-run tests when files change:

```bash
make test-watch
```

Watches:
- `tests/` directory
- `policies/` directory
- `.js` and `.json` files

### Verbose Testing

See detailed request/response for debugging:

```bash
DEBUG=* node tests/run-tests.js
```

### Manual Testing

Test a specific scenario manually:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "principal": {
      "id": "user-123",
      "userLevel": "retailer",
      "userType": "member",
      "products": ["qr"],
      "retailerId": "retail-789"
    },
    "resource": {
      "product": "qr",
      "retailerId": "retail-789"
    },
    "action": "resource:list"
  }' \
  http://localhost:3592/api/check
```

## Performance

Typical metrics:
- **18 tests**: ~2-3 seconds
- **Per test**: ~100-200ms (depends on network)
- **Node.js runner**: ~30% faster than Bash

## References

- [Test Cases](tests/README.md) — Detailed test documentation
- [Test Configuration](tests/test-cases.json) — All test scenarios
- [RBAC Model](docs/CERBOS_CONQRSE.md) — Authorization model
- [Example Scenarios](docs/CERBOS_CONQRSE_EXAMPLES.md) — Real-world examples
- [Cerbos Documentation](https://docs.cerbos.dev/)

## Support

For issues or questions:

1. Check [Troubleshooting](#troubleshooting) section
2. Review test logs: `test-results/results.json`
3. Check Cerbos logs
4. Verify policy definitions
5. Review [RBAC model](docs/CERBOS_CONQRSE.md)
