#!/usr/bin/env node

/**
 * Cerbos Policy Test Runner
 * Tests the Cerbos server against validation scenarios
 */

const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');

// Configuration
const CERBOS_URL = process.env.CERBOS_URL || 'http://localhost:3592';
const TEST_CASES_FILE = path.join(__dirname, 'test-cases.json');
const OUTPUT_DIR = process.env.OUTPUT_DIR || path.join(__dirname, '..', 'test-results');

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
};

const log = {
  info: (msg) => console.log(`${colors.blue}ℹ${colors.reset} ${msg}`),
  success: (msg) => console.log(`${colors.green}✓${colors.reset} ${msg}`),
  error: (msg) => console.log(`${colors.red}✗${colors.reset} ${msg}`),
  warn: (msg) => console.log(`${colors.yellow}⚠${colors.reset} ${msg}`),
};

// Test statistics
let stats = {
  totalSuites: 0,
  totalTests: 0,
  passed: 0,
  failed: 0,
  startTime: Date.now(),
};

/**
 * Parse URL and return protocol-specific client
 */
function getHttpClient(urlString) {
  return urlString.startsWith('https') ? https : http;
}

/**
 * Make HTTP request to Cerbos
 */
function makeRequest(url, payload) {
  return new Promise((resolve, reject) => {
    const client = getHttpClient(CERBOS_URL);
    const urlObj = new URL(url);

    const options = {
      hostname: urlObj.hostname,
      port: urlObj.port || (urlObj.protocol === 'https:' ? 443 : 80),
      path: urlObj.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(payload),
      },
      timeout: 5000,
    };

    const req = client.request(options, (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(new Error(`Failed to parse response: ${e.message}`));
        }
      });
    });

    req.on('error', reject);
    req.on('timeout', () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });

    req.write(payload);
    req.end();
  });
}

/**
 * Check Cerbos health
 */
async function checkHealth() {
  try {
    log.info(`Checking Cerbos server: ${CERBOS_URL}`);
    const healthUrl = new URL('/health', CERBOS_URL).toString();
    await makeRequest(healthUrl, '{}');
    log.success('Connected to Cerbos');
    return true;
  } catch (error) {
    log.error(`Cannot connect to Cerbos: ${error.message}`);
    return false;
  }
}

/**
 * Run a single test
 */
async function runTest(test) {
  const { id, name, principal, resource, action, expectedResult } = test;

  const payload = JSON.stringify({
    principal,
    resource,
    action,
  });

  try {
    const checkUrl = new URL('/api/check', CERBOS_URL).toString();
    const response = await makeRequest(checkUrl, payload);

    // Cerbos returns {result: {allow: true/false}}
    const allowed = response?.result?.allow;
    const actual = allowed === true ? 'ALLOW' : allowed === false ? 'DENY' : 'ERROR';

    const passed = actual === expectedResult;

    if (passed) {
      stats.passed++;
      console.log(`  ${colors.green}✓${colors.reset} ${id}: ${name}`);
    } else {
      stats.failed++;
      console.log(`  ${colors.red}✗${colors.reset} ${id}: ${name}`);
      console.log(`    Expected: ${colors.yellow}${expectedResult}${colors.reset}, Got: ${colors.red}${actual}${colors.reset}`);
    }

    return {
      id,
      name,
      expected: expectedResult,
      actual,
      status: passed ? 'PASS' : 'FAIL',
    };
  } catch (error) {
    stats.failed++;
    console.log(`  ${colors.red}✗${colors.reset} ${id}: ${name}`);
    console.log(`    Error: ${colors.red}${error.message}${colors.reset}`);
    return {
      id,
      name,
      expected: expectedResult,
      actual: 'ERROR',
      error: error.message,
      status: 'FAIL',
    };
  }
}

/**
 * Run all tests
 */
async function runAllTests() {
  // Load test cases
  if (!fs.existsSync(TEST_CASES_FILE)) {
    log.error(`Test cases file not found: ${TEST_CASES_FILE}`);
    process.exit(1);
  }

  const testData = JSON.parse(fs.readFileSync(TEST_CASES_FILE, 'utf8'));
  const testSuites = testData.testSuites;

  console.log('\n');
  console.log(`${colors.blue}${'='.repeat(48)}${colors.reset}`);
  console.log(`${colors.blue}Cerbos Policy Validation Test Runner${colors.reset}`);
  console.log(`${colors.blue}${'='.repeat(48)}${colors.reset}`);
  console.log(`\nCerbos URL: ${CERBOS_URL}`);
  console.log(`Test Cases: ${TEST_CASES_FILE}\n`);

  // Check health
  const healthy = await checkHealth();
  if (!healthy) {
    process.exit(1);
  }

  console.log('\n');

  // Run test suites
  stats.totalSuites = testSuites.length;
  const allResults = [];

  for (const suite of testSuites) {
    console.log(`${colors.yellow}=== ${suite.name} ===${colors.reset}`);
    console.log(`Description: ${suite.description}\n`);

    let suiteResults = [];
    for (const test of suite.tests) {
      stats.totalTests++;
      const result = await runTest(test);
      suiteResults.push(result);
    }

    const suitePassed = suiteResults.filter((r) => r.status === 'PASS').length;
    const suiteFailed = suiteResults.filter((r) => r.status === 'FAIL').length;

    allResults.push({
      name: suite.name,
      description: suite.description,
      results: suiteResults,
      summary: {
        total: suiteResults.length,
        passed: suitePassed,
        failed: suiteFailed,
      },
    });

    console.log(`\nSuite Results: ${colors.green}${suitePassed} passed${colors.reset}, ${colors.red}${suiteFailed} failed${colors.reset}\n`);
  }

  // Print summary
  const duration = ((Date.now() - stats.startTime) / 1000).toFixed(2);
  const successRate = ((stats.passed / stats.totalTests) * 100).toFixed(1);

  console.log(`${colors.blue}${'='.repeat(48)}${colors.reset}`);
  console.log(`${colors.blue}Test Summary${colors.reset}`);
  console.log(`${colors.blue}${'='.repeat(48)}${colors.reset}`);
  console.log(`Test Suites: ${stats.totalSuites}`);
  console.log(`Total Tests: ${stats.totalTests}`);
  console.log(`Passed: ${colors.green}${stats.passed}${colors.reset}`);
  console.log(`Failed: ${colors.red}${stats.failed}${colors.reset}`);
  console.log(`Success Rate: ${successRate}%`);
  console.log(`Duration: ${duration}s\n`);

  // Save results to JSON file
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });

  const jsonResults = {
    timestamp: new Date().toISOString(),
    cerbosUrl: CERBOS_URL,
    summary: {
      totalSuites: stats.totalSuites,
      totalTests: stats.totalTests,
      passed: stats.passed,
      failed: stats.failed,
      successRate: parseFloat(successRate),
      duration: parseFloat(duration),
    },
    suites: allResults,
  };

  const resultsFile = path.join(OUTPUT_DIR, 'results.json');
  fs.writeFileSync(resultsFile, JSON.stringify(jsonResults, null, 2));
  log.success(`Results saved to: ${resultsFile}`);

  // Exit with appropriate code
  if (stats.failed > 0) {
    log.error('Tests FAILED');
    process.exit(1);
  } else {
    log.success('All tests PASSED');
    process.exit(0);
  }
}

// Run tests
runAllTests().catch((error) => {
  log.error(`Unexpected error: ${error.message}`);
  process.exit(1);
});
