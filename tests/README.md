# Cerbos Policy Tests

This directory contains test scripts and test cases for validating the Conqrse Cerbos policies.

## Overview

The test suite validates the authorization policies against the documented scenarios in [`docs/CERBOS_CONQRSE_EXAMPLES.md`](../docs/CERBOS_CONQRSE_EXAMPLES.md).

**Test Cases**: 25 scenarios (15 ALLOW + 10 DENY)
- Covers all user levels: SU, Agency, Retailer
- Covers all user types: Owner, Admin, Lead, Member, Collaborator
- Tests direct access patterns (Act AS delegation removed)
- Validates product subscription checks
- Covers new products: Contents, Signages, Connect

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
            "roles": ["user"],
            "attr": {
              "userLevel": "retailer",
              "userType": "member",
              "name": "john.doe",
              "products": ["qr"],
              "agencyId": "agency-456",
              "retailerId": "retail-789"
            }
          },
          "resource": {
            "kind": "qr:campaigns",
            "id": "qr:campaigns",
            "attr": {
              "product": "qr",
              "retailerId": "retail-789",
              "agencyId": "agency-456"
            }
          },
          "actions": ["resource:list"],
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

### Allow Scenarios (15)

| ID | Scenario | User Level | User Type | Resource Kind | Coverage |
|---|---|---|---|---|---|
| allow_1 | Retailer Member Listing QR Campaigns | Retailer | Member | qr:campaigns | Direct access |
| allow_2 | SU Admin Managing Configuration | SU | Admin | settings:admin_users | Settings access |
| allow_3 | Agency Admin Creating QR Campaign | Agency | Admin | qr:campaigns | Direct access |
| allow_4 | Agency Owner Creating User | Agency | Owner | settings:admin_users | Settings access |
| allow_5 | SU Owner Managing System Configuration | SU | Owner | settings:admin_general | Settings access |
| allow_6 | SU Lead Viewing System Data | SU | Lead | reports:system | Read access |
| allow_7 | Agency Member Viewing Resources | Agency | Member | footprints:sites | Direct access |
| allow_8 | Retailer Owner Managing Settings | Retailer | Owner | settings:admin_general | Settings access |
| allow_9 | Retailer Owner Accessing Own Resources | Retailer | Owner | qr:campaigns | Direct access |
| allow_10 | Retailer Owner Accessing Content Templates | Retailer | Owner | contents:templates | Contents product |
| allow_11 | Retailer Member Accessing Content Assets | Retailer | Member | contents:assets | Contents product |
| allow_12 | Retailer Owner Accessing Signages People | Retailer | Owner | signages:people | Signages product |
| allow_13 | Retailer Member Accessing Signages Places Items | Retailer | Member | signages:places:item | Signages product |
| allow_14 | Retailer Admin Accessing Connect Contacts | Retailer | Admin | connect:contacts | Connect product |
| allow_15 | Retailer Owner Accessing QR Design Settings | Retailer | Owner | settings:qr_design | Settings underscore format |

### Deny Scenarios (10)

| ID | Scenario | User Level | User Type | Resource Kind | Reason |
|---|---|---|---|---|---|
| deny_1 | Retailer Collaborator Creating | Retailer | Collaborator | qr:campaigns | Read-only restriction |
| deny_2 | Product Not in Subscription | Retailer | Member | contents:templates | Product validation |
| deny_3 | SU Collaborator Creating Settings | SU | Collaborator | settings:admin_general | No settings access |
| deny_4 | Agency Lead Modifying Settings | Agency | Lead | settings:admin_users | No settings for lead |
| deny_5 | Agency Collaborator Creating | Agency | Collaborator | qr:campaigns | Read-only restriction |
| deny_6 | Retailer Lead Modifying Settings | Retailer | Lead | settings:admin_general | No settings for lead |
| deny_7 | Retailer Isolation Cross-Retailer | Retailer | Owner | qr:campaigns | Cross-retailer blocked |
| deny_8 | Retailer Isolation Cross-Retailer Footprints | Retailer | Member | footprints:sites | Cross-retailer blocked |
| deny_9 | Agency Member Contents Without Subscription | Agency | Member | contents:assets | Product validation |
| deny_10 | Retailer Collaborator Modifying Signages | Retailer | Collaborator | signages:people | Read-only restriction |

## Cerbos API

Tests communicate with Cerbos via the HTTP API:

```
POST /api/check
Content-Type: application/json

{
  "principal": {
    "id": "user-123",
    "roles": ["user"],
    "attr": {
      "userLevel": "retailer",
      "userType": "member",
      "name": "john.doe",
      "products": ["qr"],
      "agencyId": "agency-456",
      "retailerId": "retail-789"
    }
  },
  "resource": {
    "kind": "qr:campaigns",
    "id": "qr:campaigns",
    "attr": {
      "product": "qr",
      "retailerId": "retail-789",
      "agencyId": "agency-456"
    }
  },
  "actions": ["resource:list"]
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

### Principal Attributes

- **id**: Unique identifier for the user
- **roles**: Array of role identifiers (always `["user"]` for Conqrse)
- **attr**: User attributes object containing:
  - **userLevel**: One of `su`, `agency`, `retailer`
  - **userType**: One of `owner`, `admin`, `lead`, `member`, `collaborator`
  - **name**: User's display name or email
  - **products**: Array of subscribed products (e.g., `qr`, `footprints`, `signages`, `contents`, `connect`, `reports`)
  - **agencyId**: Agency identifier (only for agency/retailer users)
  - **retailerId**: Retailer identifier (only for retailer users)

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
  "principal": {
    "id": "user-123",
    "roles": ["user"],
    "attr": {
      "userLevel": "retailer",
      "userType": "owner",
      "name": "user@retailer.com",
      "products": ["qr"],
      "agencyId": "agency-456",
      "retailerId": "retail-789"
    }
  },
  "resource": {
    "kind": "qr:campaigns",
    "id": "qr:campaigns",
    "attr": {
      "product": "qr",
      "retailerId": "retail-789",
      "agencyId": "agency-456"
    }
  },
  "actions": ["resource:view"],
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
