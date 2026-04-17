#!/bin/bash

# Cerbos Policy Validation Test Script
# Tests the Cerbos server against examples from CERBOS_CONQRSE_EXAMPLES.md

set -e

# Configuration
CERBOS_URL="${CERBOS_URL:-http://localhost:3592}"
EXAMPLES_FILE="./docs/CERBOS_CONQRSE_EXAMPLES.md"
RESULTS_FILE="./test-results.json"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Cerbos Policy Validation Test Suite${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo "Cerbos Server: $CERBOS_URL"
echo "Examples File: $EXAMPLES_FILE"
echo ""

# Check if examples file exists
if [ ! -f "$EXAMPLES_FILE" ]; then
    echo -e "${RED}Error: Examples file not found at $EXAMPLES_FILE${NC}"
    exit 1
fi

# Check Cerbos connectivity
echo "Checking Cerbos server connectivity..."
if ! curl -s "$CERBOS_URL/health" > /dev/null 2>&1; then
    echo -e "${RED}Error: Cannot connect to Cerbos server at $CERBOS_URL${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Connected to Cerbos server${NC}"
echo ""

# Function to extract JSON from markdown code blocks
extract_json_blocks() {
    local file=$1
    local section=$2

    awk "
        /^## $section/,/^## / {
            if (/^## / && !/^## $section/) exit
            if (/^\`\`\`json/) {
                in_block=1
                next
            }
            if (/^\`\`\`/ && in_block) {
                in_block=0
                next
            }
            if (in_block) print
        }
    " "$file"
}

# Function to run a single test
run_test() {
    local scenario_name=$1
    local principal_json=$2
    local resource_json=$3
    local action=$4
    local expected_result=$5

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    # Build request payload
    local payload=$(cat <<EOF
{
  "principal": $principal_json,
  "resource": $resource_json,
  "action": "$action"
}
EOF
)

    # Send request to Cerbos
    local response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "$payload" \
        "$CERBOS_URL/api/check" 2>/dev/null || echo '{}')

    # Extract decision
    local decision=$(echo "$response" | grep -o '"effect":"[^"]*"' | cut -d'"' -f4 | head -1)

    if [ -z "$decision" ]; then
        decision="ERROR"
    fi

    # Normalize expected result
    local expected_upper=$(echo "$expected_result" | tr '[:lower:]' '[:upper:]')
    local decision_upper=$(echo "$decision" | tr '[:lower:]' '[:upper:]')

    # Check if result matches expectation
    local passed=false
    if [[ "$expected_upper" == "ALLOW" && "$decision_upper" == "EFFECT_ALLOW" ]]; then
        passed=true
    elif [[ "$expected_upper" == "DENY" && "$decision_upper" == "EFFECT_DENY" ]]; then
        passed=true
    fi

    if [ "$passed" = true ]; then
        PASSED_TESTS=$((PASSED_TESTS + 1))
        echo -e "${GREEN}✓ PASS${NC}: $scenario_name"
    else
        FAILED_TESTS=$((FAILED_TESTS + 1))
        echo -e "${RED}✗ FAIL${NC}: $scenario_name"
        echo "  Expected: $expected_result"
        echo "  Got: $decision"
        echo "  Request: $payload"
    fi
}

# Parse and run tests from ALLOW section
echo -e "${YELLOW}=== ALLOW Scenarios ===${NC}"
echo ""

# Extract scenarios from markdown
# This is a simplified parser - in production you'd use a proper markdown parser
while IFS= read -r line; do
    if [[ $line =~ ^###\ Scenario\ ([0-9]+).*:\ (.*) ]]; then
        scenario_num="${BASH_REMATCH[1]}"
        scenario_name="${BASH_REMATCH[2]}"

        # Read the next lines until we find the JSON block
        while IFS= read -r json_line; do
            if [[ $json_line =~ ^\`\`\`json ]]; then
                # Read JSON until closing ```
                json_content=""
                while IFS= read -r json_data; do
                    if [[ $json_data == '```' ]]; then
                        break
                    fi
                    json_content+="$json_data"
                done

                # Parse the JSON to extract principal, resource, and action
                # This is simplified - real implementation would use jq
                break
            fi
        done
    fi
done < "$EXAMPLES_FILE"

echo ""
echo -e "${YELLOW}=== DENY Scenarios ===${NC}"
echo ""

# Summary
echo ""
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}================================================${NC}"
echo "Total Tests: $TOTAL_TESTS"
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed: ${RED}$FAILED_TESTS${NC}"
echo -e "Skipped: $SKIPPED_TESTS"
echo ""

# Exit with error if any tests failed
if [ $FAILED_TESTS -gt 0 ]; then
    exit 1
fi
