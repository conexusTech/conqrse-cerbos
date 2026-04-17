#!/bin/bash

# Cerbos Policy Test Runner
# Executes tests from test-cases.json against a running Cerbos server

set -e

# Configuration
CERBOS_URL="${CERBOS_URL:-http://localhost:3592}"
TEST_CASES_FILE="./tests/test-cases.json"
OUTPUT_DIR="${OUTPUT_DIR:-./test-results}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
TOTAL_SUITES=0
TOTAL_TESTS=0
PASSED=0
FAILED=0

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Cerbos Policy Validation Test Runner${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo "Cerbos URL: $CERBOS_URL"
echo "Test Cases: $TEST_CASES_FILE"
echo "Output Dir: $OUTPUT_DIR"
echo ""

# Check Cerbos connectivity
echo "Checking Cerbos server connectivity..."
if ! curl -s -m 5 "$CERBOS_URL/health" > /dev/null 2>&1; then
    echo -e "${RED}✗ Error: Cannot connect to Cerbos server at $CERBOS_URL${NC}"
    echo "  Make sure Cerbos is running and accessible"
    exit 1
fi
echo -e "${GREEN}✓ Connected to Cerbos${NC}"
echo ""

# Check test cases file exists
if [ ! -f "$TEST_CASES_FILE" ]; then
    echo -e "${RED}✗ Error: Test cases file not found: $TEST_CASES_FILE${NC}"
    exit 1
fi

# Process test suites
SUITE_COUNT=$(jq '.testSuites | length' "$TEST_CASES_FILE")

for ((i=0; i<SUITE_COUNT; i++)); do
    SUITE=$(jq ".testSuites[$i]" "$TEST_CASES_FILE")
    SUITE_NAME=$(echo "$SUITE" | jq -r '.name')
    SUITE_DESC=$(echo "$SUITE" | jq -r '.description')
    TEST_COUNT=$(echo "$SUITE" | jq '.tests | length')

    TOTAL_SUITES=$((TOTAL_SUITES + 1))

    echo -e "${YELLOW}=== $SUITE_NAME ===${NC}"
    echo "Description: $SUITE_DESC"
    echo ""

    SUITE_PASSED=0
    SUITE_FAILED=0
    SUITE_RESULTS=()

    for ((j=0; j<TEST_COUNT; j++)); do
        TEST=$(echo "$SUITE" | jq ".tests[$j]")
        TEST_ID=$(echo "$TEST" | jq -r '.id')
        TEST_NAME=$(echo "$TEST" | jq -r '.name')
        PRINCIPAL=$(echo "$TEST" | jq '.principal')
        RESOURCE=$(echo "$TEST" | jq '.resource')
        ACTION=$(echo "$TEST" | jq -r '.action')
        EXPECTED=$(echo "$TEST" | jq -r '.expectedResult')

        TOTAL_TESTS=$((TOTAL_TESTS + 1))

        # Build request payload
        PAYLOAD=$(jq -n \
            --argjson principal "$PRINCIPAL" \
            --argjson resource "$RESOURCE" \
            --arg action "$ACTION" \
            '{principal: $principal, resource: $resource, action: $action}')

        # Send to Cerbos
        RESPONSE=$(curl -s -X POST \
            -H "Content-Type: application/json" \
            -d "$PAYLOAD" \
            "$CERBOS_URL/api/check" 2>/dev/null || echo '{}')

        # Extract decision
        DECISION=$(echo "$RESPONSE" | jq -r '.result.allow // empty')

        if [ -z "$DECISION" ]; then
            DECISION="ERROR"
        fi

        # Normalize comparison (true/false vs ALLOW/DENY)
        if [ "$DECISION" = "true" ]; then
            DECISION="ALLOW"
        elif [ "$DECISION" = "false" ]; then
            DECISION="DENY"
        fi

        # Check result
        if [ "$DECISION" = "$EXPECTED" ]; then
            PASSED=$((PASSED + 1))
            SUITE_PASSED=$((SUITE_PASSED + 1))
            echo -e "  ${GREEN}✓${NC} $TEST_ID: $TEST_NAME"
            RESULT_STATUS="PASS"
        else
            FAILED=$((FAILED + 1))
            SUITE_FAILED=$((SUITE_FAILED + 1))
            echo -e "  ${RED}✗${NC} $TEST_ID: $TEST_NAME"
            echo -e "    Expected: ${YELLOW}$EXPECTED${NC}, Got: ${RED}$DECISION${NC}"
            RESULT_STATUS="FAIL"
        fi

        # Store result for JSON output
        SUITE_RESULTS+=("{\"id\":\"$TEST_ID\",\"name\":\"$TEST_NAME\",\"expected\":\"$EXPECTED\",\"actual\":\"$DECISION\",\"status\":\"$RESULT_STATUS\"}")
    done

    echo ""
    echo "Suite Results: ${GREEN}$SUITE_PASSED passed${NC}, ${RED}$SUITE_FAILED failed${NC}"
    echo ""
done

# Summary
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}================================================${NC}"
echo "Test Suites: $TOTAL_SUITES"
echo "Total Tests: $TOTAL_TESTS"
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo "Success Rate: $(awk "BEGIN {printf \"%.1f%%\", ($PASSED/$TOTAL_TESTS)*100}")"
echo ""

# Generate JSON results file
RESULTS_JSON=$(cat <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "cerbosUrl": "$CERBOS_URL",
  "summary": {
    "totalSuites": $TOTAL_SUITES,
    "totalTests": $TOTAL_TESTS,
    "passed": $PASSED,
    "failed": $FAILED,
    "successRate": $(awk "BEGIN {printf \"%.2f\", ($PASSED/$TOTAL_TESTS)*100}")
  }
}
EOF
)

echo "$RESULTS_JSON" | jq . > "$OUTPUT_DIR/results.json"
echo -e "${GREEN}✓ Results saved to: $OUTPUT_DIR/results.json${NC}"
echo ""

# Exit with error if any tests failed
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Tests FAILED${NC}"
    exit 1
else
    echo -e "${GREEN}All tests PASSED${NC}"
    exit 0
fi
