# Cerbos Policy Tests

This directory contains test scripts and test cases for validating the Conqrse Cerbos policies.

## Overview

The test suite validates the authorization policies against the documented scenarios in [`docs/CERBOS_CONQRSE_EXAMPLES.md`](../docs/CERBOS_CONQRSE_EXAMPLES.md).

**Test Cases**: 18 scenarios (10 ALLOW + 8 DENY)
- Covers all user levels: SU, Agency, Retailer
- Covers all user types: Owner, Admin, Lead, Member, Collaborator
- Tests direct access and "Act AS" delegation patterns
- Validates product subscription checks

## Files

- **`test-cases.json`** — Structured test case definitions
- **`run-tests.sh`** — Bash test runner (uses curl)
- **`validate-policies.sh`** — Legacy bash parser (WIP)

## Quick Start

### Prerequisites

- Cerbos server running and accessible
- Node.js 14+ (for JavaScript runner) OR bash with jq (for shell runner)

### Running Tests

```bash
# Run tests with default Cerbos URL
./tests/run-tests.sh

# With custom Cerbos URL
CERBOS_URL=http://cerbos.example.com:3592 ./tests/run-tests.sh

# With custom output directory
OUTPUT_DIR=./custom-results ./tests/run-tests.sh
```

## Test Cases Structure

Test cases are defined in `test-cases.json` with the following structure:

```json
{
  "testSuites": [
    {
      "name": "Allow Scenarios",
      "description": "Valid access patterns that should ALLOW",
      "tests": [
        {
          "id": "allow_1",
          "name": "Retailer Member Listing QR Campaigns",
          "description": "Retailer-level user viewing campaigns in their own retailer",
          "principal": {
            "id": "user-123",
            "userLevel": "retailer",
            "userType": "member",
            "products": ["qr"],
            "agencyId": "agency-456",
            "retailerId": "retail-789"
          },
          "resource": {
            "name": "qr:campaigns",
            "product": "qr",
            "retailerId": "retail-789"
          },
          "action": "resource:list",
          "expectedResult": "ALLOW"
        }
      ]
    }
  ]
}
```

## Test Results

After running tests, results are saved to `test-results/results.json`:

```json
{
  "timestamp": "2026-04-15T12:34:56Z",
  "cerbosUrl": "http://localhost:3592",
  "summary": {
    "totalSuites": 2,
    "totalTests": 18,
    "passed": 18,
    "failed": 0,
    "successRate": 100.0,
    "duration": 2.34
  },
  "suites": [
    {
      "name": "Allow Scenarios",
      "description": "Valid access patterns that should ALLOW",
      "results": [
        {
          "id": "allow_1",
          "name": "Retailer Member Listing QR Campaigns",
          "expected": "ALLOW",
          "actual": "ALLOW",
          "status": "PASS"
        }
      ],
      "summary": {
        "total": 10,
        "passed": 10,
        "failed": 0
      }
    }
  ]
}
```

## Scenario Coverage

### Allow Scenarios (10)

| ID | Scenario | User Level | User Type | Pattern |
|---|---|---|---|---|
| allow_1 | Retailer Member Listing QR Campaigns | Retailer | Member | Direct access |
| allow_2 | SU Admin Acting AS Retailer Admin | SU | Admin | Act AS delegation |
| allow_3 | Agency Admin Acting AS Retailer | Agency | Admin | Act AS delegation |
| allow_4 | Agency Owner Creating User | Agency | Owner | Direct access |
| allow_5 | SU Owner Managing Settings | SU | Owner | Settings access |
| allow_6 | SU Lead Viewing Data | SU | Lead | Read access |
| allow_7 | SU Collaborator Acting AS Retailer | SU | Collaborator | Delegated read-only |
| allow_8 | Agency Lead Acting AS Retailer | Agency | Lead | Act AS delegation |
| allow_9 | Agency Member Viewing Resources | Agency | Member | Direct access |
| allow_10 | Retailer Owner Managing Settings | Retailer | Owner | Settings access |

### Deny Scenarios (8)

| ID | Scenario | User Level | User Type | Reason |
|---|---|---|---|---|
| deny_1 | Retailer Collaborator Creating | Retailer | Collaborator | Read-only restriction |
| deny_2 | Product Not in Subscription | Retailer | Member | Product validation |
| deny_3 | SU Collaborator Creating Settings | SU | Collaborator | No settings access |
| deny_4 | Agency Lead Modifying Settings | Agency | Lead | No settings for lead |
| deny_5 | Agency Collaborator Creating | Agency | Collaborator | Read-only restriction |
| deny_6 | Retailer Lead Modifying Settings | Retailer | Lead | No settings for lead |
| deny_7 | Acting AS Unrelated Retailer | Agency | Admin | Not child retailer |
| deny_8 | Retailer Acting AS Another | Retailer | Member | Cannot delegate |

## Cerbos API

Tests communicate with Cerbos via the HTTP API:

```
POST /api/check
Content-Type: application/json

{
  "principal": {
    "id": "user-123",
    "userLevel": "retailer",
    "userType": "member",
    "products": ["qr"],
    "agencyId": "agency-456",
    "retailerId": "retail-789"
  },
  "resource": {
    "name": "qr:campaigns",
    "product": "qr",
    "retailerId": "retail-789"
  },
  "action": "resource:list"
}
```

Response:
```json
{
  "result": {
    "allow": true
  }
}
```

## Extending Tests

To add new test cases:

1. Edit `test-cases.json`
2. Add test to appropriate `testSuites` array
3. Use principal/resource/action from the scenario
4. Set `expectedResult` to `ALLOW` or `DENY`
5. Run tests to validate

Example:

```json
{
  "id": "allow_custom",
  "name": "My Custom Test",
  "description": "Description of what this tests",
  "principal": { /* ... */ },
  "resource": { /* ... */ },
  "action": "resource:view",
  "expectedResult": "ALLOW"
}
```

## Troubleshooting

### Cannot connect to Cerbos
- Verify Cerbos server is running: `curl http://localhost:3592/health`
- Check `CERBOS_URL` environment variable
- For remote servers: `CERBOS_URL=https://cerbos.example.com node tests/run-tests.js`

### Test failures
- Check Cerbos logs for policy evaluation errors
- Verify principal attributes match derived role conditions in policies
- Check resource attributes are correctly formatted
- Review policy definitions in `policies/` directory

### Permission errors
- Ensure test runner has access to write to `test-results/` directory

## Integration

### CI/CD Pipeline

Add to your CI configuration:

```yaml
# GitHub Actions
- name: Test Cerbos Policies
  run: node tests/run-tests.js
  env:
    CERBOS_URL: ${{ secrets.CERBOS_URL }}

# GitLab CI
test_cerbos:
  script:
    - node tests/run-tests.js
  variables:
    CERBOS_URL: $CI_CERBOS_URL
```

### Package.json Scripts

Add to `package.json`:

```json
{
  "scripts": {
    "test:cerbos": "node tests/run-tests.js",
    "test:cerbos:watch": "nodemon --watch tests --watch policies tests/run-tests.js"
  }
}
```

## Monitoring

Monitor test results in your deployment pipeline:

- Check `test-results/results.json` after each run
- Parse `summary.successRate` to alert on regressions
- Log failures for debugging
- Track duration trends over time

## Performance

Typical test execution:
- 18 tests in ~2-3 seconds (depends on network latency)
- Each test makes one HTTP request to Cerbos
- Node.js runner is ~30% faster than bash runner

## References

- [Cerbos Policy Language](https://docs.cerbos.dev/cerbos/latest/policies.html)
- [Cerbos API](https://docs.cerbos.dev/cerbos/latest/api.html)
- [Conqrse RBAC Model](../docs/CERBOS_CONQRSE.md)
- [Example Scenarios](../docs/CERBOS_CONQRSE_EXAMPLES.md)
