#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const http = require('http');
const https = require('https');
const yaml = require('js-yaml');

const CERBOS_URL = process.env.CERBOS_BASE_URL || 'http://localhost:3592';
const USERNAME = process.env.CERBOS_ADMIN_USERNAME || 'cerbos';
const PASSWORD = process.env.CERBOS_ADMIN_PASSWORD || 'conqrseCerbos';
const POLICIES_DIR = '/policies-seed';
const MAX_RETRIES = 30;
const RETRY_DELAY = 1000;

const credentials = Buffer.from(`${USERNAME}:${PASSWORD}`).toString('base64');

async function waitForCerbos() {
  for (let i = 0; i < MAX_RETRIES; i++) {
    try {
      await makeRequest('GET', '/_cerbos/health');
      console.log('✓ Cerbos is ready');
      return;
    } catch (error) {
      if (i < MAX_RETRIES - 1) {
        console.log(`Waiting for Cerbos... (${i + 1}/${MAX_RETRIES})`);
        await sleep(RETRY_DELAY);
      }
    }
  }
  throw new Error('Cerbos did not become ready in time');
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function makeRequest(method, path, body = null) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(path, CERBOS_URL);
    const options = {
      hostname: urlObj.hostname,
      port: urlObj.port,
      path: urlObj.pathname + urlObj.search,
      method: method,
      headers: {
        'Authorization': `Basic ${credentials}`,
        'Content-Type': 'application/json',
      },
    };

    if (body) {
      const bodyStr = JSON.stringify(body);
      options.headers['Content-Length'] = Buffer.byteLength(bodyStr);
    }

    const protocol = urlObj.protocol === 'https:' ? https : http;
    const req = protocol.request(options, (res) => {
      let data = '';
      res.on('data', chunk => { data += chunk; });
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve({ status: res.statusCode, data });
        } else {
          reject(new Error(`HTTP ${res.statusCode}: ${data}`));
        }
      });
    });

    req.on('error', reject);

    if (body) {
      req.write(JSON.stringify(body));
    }
    req.end();
  });
}

async function seedPolicy(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    const policy = yaml.load(content);

    if (!policy) {
      console.warn(`⚠ Empty policy file: ${path.basename(filePath)}`);
      return;
    }

    await makeRequest('POST', '/admin/policy', { policies: [policy] });
    console.log(`✓ Seeded: ${path.basename(filePath)}`);
  } catch (error) {
    console.error(`✗ Failed to seed ${path.basename(filePath)}: ${error.message}`);
    throw error;
  }
}

async function main() {
  try {
    console.log('Cerbos Policy Seeding Script');
    console.log('=============================\n');

    if (!fs.existsSync(POLICIES_DIR)) {
      console.log(`ℹ No policies directory found (${POLICIES_DIR}). Skipping seeding.`);
      process.exit(0);
    }

    console.log('Waiting for Cerbos to be ready...');
    await waitForCerbos();

    const files = fs.readdirSync(POLICIES_DIR)
      .filter(f => f.endsWith('.yaml') || f.endsWith('.yml'))
      .sort();

    if (files.length === 0) {
      console.log('No policy files found. Skipping seeding.');
      process.exit(0);
    }

    console.log(`\nSeeding ${files.length} policy file(s)...\n`);

    for (const file of files) {
      const filePath = path.join(POLICIES_DIR, file);
      await seedPolicy(filePath);
    }

    console.log('\n✓ Policy seeding completed successfully');
    process.exit(0);
  } catch (error) {
    console.error('\n✗ Policy seeding failed:', error.message);
    process.exit(1);
  }
}

main();
