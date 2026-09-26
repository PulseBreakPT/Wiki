"""Test offline query contracts in frontend/src/lib/offline.ts.

Tests search (Jason, accent Lucia/Ambrósia, fuzzy Jsaon, empty/no results),
type filters (personagem/local), labels, ids, pagination sorted no duplicates/cursor total,
version1/history/invalid slug/version, read-only/auth rejection and AbortSignal,
no network API calls.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OFFLINE_TS = ROOT / 'frontend' / 'src' / 'lib' / 'offline.ts'
ARCHIVE_JSON = ROOT / 'frontend' / 'public' / 'data' / 'archive.json'

class TestResults:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
    
    def add_pass(self, test_name, details=""):
        self.passed.append((test_name, details))
        print(f"✅ PASS: {test_name}")
        if details:
            print(f"   {details}")
    
    def add_fail(self, test_name, details):
        self.failed.append((test_name, details))
        print(f"❌ FAIL: {test_name}")
        print(f"   {details}")
    
    def add_warning(self, test_name, details):
        self.warnings.append((test_name, details))
        print(f"⚠️  WARNING: {test_name}")
        print(f"   {details}")
    
    def summary(self):
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"✅ Passed: {len(self.passed)}")
        print(f"❌ Failed: {len(self.failed)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        return len(self.failed) == 0

def create_test_harness():
    """Create a Node.js test harness to execute offline.ts query logic."""
    harness_code = """
const fs = require('fs');
const path = require('path');

// Mock fetch to load local archive.json
global.fetch = async (url) => {
  if (url === '/data/archive.json') {
    const archivePath = path.join(__dirname, '../frontend/public/data/archive.json');
    const data = JSON.parse(fs.readFileSync(archivePath, 'utf-8'));
    return {
      ok: true,
      json: async () => data
    };
  }
  throw new Error(`Unexpected fetch: ${url}`);
};

// Mock process.env
process.env.REACT_APP_OFFLINE = 'true';

// Load and transpile offline.ts
const ts = require('typescript');
const offlineTsPath = path.join(__dirname, '../frontend/src/lib/offline.ts');
const typesPath = path.join(__dirname, '../frontend/src/types.ts');

// Read type definitions
const typesContent = fs.readFileSync(typesPath, 'utf-8');
const offlineContent = fs.readFileSync(offlineTsPath, 'utf-8');

// Transpile TypeScript to JavaScript
const typesJs = ts.transpileModule(typesContent, {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 }
}).outputText;

const offlineJs = ts.transpileModule(offlineContent, {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 }
}).outputText;

// Execute transpiled code
eval(typesJs);
const offlineModule = {};
eval(offlineJs.replace(/export /g, 'offlineModule.'));

const offlineRequest = offlineModule.offlineRequest;

// Test runner
async function runTests() {
  const results = { passed: 0, failed: 0, tests: [] };
  
  async function test(name, fn) {
    try {
      await fn();
      results.passed++;
      results.tests.push({ name, status: 'PASS' });
      console.log(`✅ PASS: ${name}`);
    } catch (error) {
      results.failed++;
      results.tests.push({ name, status: 'FAIL', error: error.message });
      console.log(`❌ FAIL: ${name}`);
      console.log(`   ${error.message}`);
    }
  }
  
  // Test 1: Search for "Jason"
  await test('Search for Jason', async () => {
    const result = await offlineRequest('/entities?q=jason');
    if (!result.items || result.items.length === 0) {
      throw new Error('No results for Jason search');
    }
    const jasonFound = result.items.some(e => e.name.includes('Jason'));
    if (!jasonFound) {
      throw new Error('Jason not found in search results');
    }
  });
  
  // Test 2: Search with accent - Lucia
  await test('Search for Lucia (accent)', async () => {
    const result = await offlineRequest('/entities?q=Lúcia');
    if (!result.items || result.items.length === 0) {
      throw new Error('No results for Lúcia search');
    }
    const luciaFound = result.items.some(e => e.name.includes('Lucia'));
    if (!luciaFound) {
      throw new Error('Lucia not found in accent search');
    }
  });
  
  // Test 3: Search with accent - Ambrosia
  await test('Search for Ambrósia (accent)', async () => {
    const result = await offlineRequest('/entities?q=Ambrósia');
    if (!result.items || result.items.length === 0) {
      throw new Error('No results for Ambrósia search');
    }
    const ambrosiaFound = result.items.some(e => e.name === 'Ambrosia');
    if (!ambrosiaFound) {
      throw new Error('Ambrosia not found in accent search');
    }
  });
  
  // Test 4: Fuzzy search - "Jsaon" should suggest "Jason"
  await test('Fuzzy search for Jsaon', async () => {
    const result = await offlineRequest('/entities?q=Jsaon');
    if (!result.suggestion) {
      throw new Error('No suggestion for fuzzy search "Jsaon"');
    }
    if (!result.suggestion.toLowerCase().includes('jason')) {
      throw new Error(`Expected Jason suggestion, got: ${result.suggestion}`);
    }
  });
  
  // Test 5: Empty search results
  await test('Empty search results', async () => {
    const result = await offlineRequest('/entities?q=nonexistentxyz123');
    if (result.items.length !== 0) {
      throw new Error('Expected empty results for nonexistent search');
    }
    if (result.total !== 0) {
      throw new Error('Expected total=0 for empty results');
    }
  });
  
  // Test 6: Filter by type - personagem
  await test('Filter by type personagem', async () => {
    const result = await offlineRequest('/entities?type=personagem');
    if (!result.items || result.items.length === 0) {
      throw new Error('No results for type=personagem');
    }
    const allPersonagem = result.items.every(e => e.type === 'personagem');
    if (!allPersonagem) {
      throw new Error('Not all results are type personagem');
    }
  });
  
  // Test 7: Filter by type - local
  await test('Filter by type local', async () => {
    const result = await offlineRequest('/entities?type=local');
    if (!result.items || result.items.length === 0) {
      throw new Error('No results for type=local');
    }
    const allLocal = result.items.every(e => e.type === 'local');
    if (!allLocal) {
      throw new Error('Not all results are type local');
    }
  });
  
  // Test 8: Filter by label
  await test('Filter by label Official', async () => {
    const result = await offlineRequest('/entities?label=Official');
    if (!result.items || result.items.length === 0) {
      throw new Error('No results for label=Official');
    }
    const allOfficial = result.items.every(e => e.label === 'Official');
    if (!allOfficial) {
      throw new Error('Not all results have label Official');
    }
  });
  
  // Test 9: Filter by IDs
  await test('Filter by IDs', async () => {
    const result = await offlineRequest('/entities?ids=jason-duval,lucia-caminos');
    if (result.items.length !== 2) {
      throw new Error(`Expected 2 results, got ${result.items.length}`);
    }
    const ids = result.items.map(e => e.id).sort();
    if (ids[0] !== 'jason-duval' || ids[1] !== 'lucia-caminos') {
      throw new Error(`Unexpected IDs: ${ids}`);
    }
  });
  
  // Test 10: Pagination - sorted results
  await test('Pagination sorted results', async () => {
    const result = await offlineRequest('/entities?limit=5');
    if (result.items.length > 5) {
      throw new Error(`Expected max 5 results, got ${result.items.length}`);
    }
    const slugs = result.items.map(e => e.slug);
    const sortedSlugs = [...slugs].sort();
    if (JSON.stringify(slugs) !== JSON.stringify(sortedSlugs)) {
      throw new Error('Results not sorted by slug');
    }
  });
  
  // Test 11: Pagination - no duplicates
  await test('Pagination no duplicates', async () => {
    const result = await offlineRequest('/entities?limit=20');
    const ids = result.items.map(e => e.id);
    const uniqueIds = [...new Set(ids)];
    if (ids.length !== uniqueIds.length) {
      throw new Error('Duplicate IDs found in results');
    }
  });
  
  // Test 12: Pagination - cursor
  await test('Pagination with cursor', async () => {
    const page1 = await offlineRequest('/entities?limit=3');
    if (!page1.next_cursor) {
      throw new Error('Expected next_cursor for first page');
    }
    const page2 = await offlineRequest(`/entities?limit=3&cursor=${page1.next_cursor}`);
    const page1Ids = page1.items.map(e => e.id);
    const page2Ids = page2.items.map(e => e.id);
    const overlap = page1Ids.filter(id => page2Ids.includes(id));
    if (overlap.length > 0) {
      throw new Error('Cursor pagination has overlapping results');
    }
  });
  
  // Test 13: Pagination - total count
  await test('Pagination total count', async () => {
    const result = await offlineRequest('/entities?limit=5');
    if (typeof result.total !== 'number') {
      throw new Error('Missing total count');
    }
    if (result.total !== 12) {
      throw new Error(`Expected total=12, got ${result.total}`);
    }
  });
  
  // Test 14: Entity detail by slug
  await test('Entity detail jason-duval', async () => {
    const result = await offlineRequest('/entities/jason-duval');
    if (result.id !== 'jason-duval') {
      throw new Error('Wrong entity returned');
    }
    if (!result.assertions || result.assertions.length === 0) {
      throw new Error('Entity missing assertions');
    }
    if (!result.related) {
      throw new Error('Entity missing related field');
    }
  });
  
  // Test 15: Entity detail with version
  await test('Entity detail with version=1', async () => {
    const result = await offlineRequest('/entities/jason-duval?version=1');
    if (result.version !== 1) {
      throw new Error('Wrong version returned');
    }
  });
  
  // Test 16: Entity detail with invalid version
  await test('Entity detail with invalid version', async () => {
    try {
      await offlineRequest('/entities/jason-duval?version=2');
      throw new Error('Should have thrown error for invalid version');
    } catch (error) {
      if (!error.message.includes('não está incluída')) {
        throw new Error(`Wrong error message: ${error.message}`);
      }
    }
  });
  
  // Test 17: Entity history
  await test('Entity history', async () => {
    const result = await offlineRequest('/entities/jason-duval/history');
    if (!Array.isArray(result)) {
      throw new Error('History should be an array');
    }
    if (result.length === 0) {
      throw new Error('History should not be empty');
    }
    if (result[0].version !== 1) {
      throw new Error('History version should be 1');
    }
  });
  
  // Test 18: Invalid entity slug
  await test('Invalid entity slug', async () => {
    try {
      await offlineRequest('/entities/nonexistent-entity');
      throw new Error('Should have thrown error for invalid slug');
    } catch (error) {
      if (!error.message.includes('não existe')) {
        throw new Error(`Wrong error message: ${error.message}`);
      }
    }
  });
  
  // Test 19: Stats endpoint
  await test('Stats endpoint', async () => {
    const result = await offlineRequest('/stats');
    if (!result.entities || !result.sources || !result.assertions) {
      throw new Error('Stats missing required fields');
    }
    if (result.entities !== 12) {
      throw new Error(`Expected 12 entities in stats, got ${result.entities}`);
    }
  });
  
  // Test 20: Featured endpoint
  await test('Featured endpoint', async () => {
    const result = await offlineRequest('/featured');
    if (!Array.isArray(result)) {
      throw new Error('Featured should be an array');
    }
    if (result.length !== 4) {
      throw new Error(`Expected 4 featured entities, got ${result.length}`);
    }
  });
  
  // Test 21: Timeline endpoint
  await test('Timeline endpoint', async () => {
    const result = await offlineRequest('/timeline');
    if (!Array.isArray(result)) {
      throw new Error('Timeline should be an array');
    }
    if (result.length !== 2) {
      throw new Error(`Expected 2 timeline entries, got ${result.length}`);
    }
  });
  
  // Test 22: Sources endpoint (only referenced sources)
  await test('Sources endpoint', async () => {
    const result = await offlineRequest('/sources');
    if (!Array.isArray(result)) {
      throw new Error('Sources should be an array');
    }
    if (result.length !== 2) {
      throw new Error(`Expected 2 referenced sources, got ${result.length}`);
    }
  });
  
  // Test 23: Auth rejection
  await test('Auth endpoint rejection', async () => {
    try {
      await offlineRequest('/auth/me');
      throw new Error('Should have thrown error for auth endpoint');
    } catch (error) {
      if (!error.message.includes('não estão disponíveis')) {
        throw new Error(`Wrong error message: ${error.message}`);
      }
    }
  });
  
  // Test 24: Editorial rejection
  await test('Editorial endpoint rejection', async () => {
    try {
      await offlineRequest('/editorial/drafts');
      throw new Error('Should have thrown error for editorial endpoint');
    } catch (error) {
      if (!error.message.includes('não estão disponíveis')) {
        throw new Error(`Wrong error message: ${error.message}`);
      }
    }
  });
  
  // Test 25: POST method rejection
  await test('POST method rejection', async () => {
    try {
      await offlineRequest('/entities', { method: 'POST' });
      throw new Error('Should have thrown error for POST method');
    } catch (error) {
      if (!error.message.includes('não estão disponíveis')) {
        throw new Error(`Wrong error message: ${error.message}`);
      }
    }
  });
  
  // Test 26: AbortSignal support
  await test('AbortSignal support', async () => {
    const controller = new AbortController();
    controller.abort();
    try {
      await offlineRequest('/entities', { signal: controller.signal });
      throw new Error('Should have thrown AbortError');
    } catch (error) {
      if (error.name !== 'AbortError') {
        throw new Error(`Expected AbortError, got ${error.name}`);
      }
    }
  });
  
  return results;
}

// Run tests and output results
runTests().then(results => {
  console.log('\\n' + '='.repeat(80));
  console.log('TEST SUMMARY');
  console.log('='.repeat(80));
  console.log(`✅ Passed: ${results.passed}`);
  console.log(`❌ Failed: ${results.failed}`);
  process.exit(results.failed > 0 ? 1 : 0);
}).catch(error => {
  console.error('Test harness error:', error);
  process.exit(1);
});
"""
    
    harness_path = ROOT / 'tests' / 'offline_query_harness.js'
    harness_path.write_text(harness_code)
    return harness_path

def test_offline_query_contracts(results):
    """Test offline query contracts using Node.js harness."""
    print("\n--- Testing Offline Query Contracts ---")
    
    # Create test harness
    harness_path = create_test_harness()
    
    # Set NODE_PATH to include frontend node_modules
    import os
    env = os.environ.copy()
    env['NODE_PATH'] = str(ROOT / 'frontend' / 'node_modules')
    
    # Run the harness
    result = subprocess.run(['node', str(harness_path)], 
                          capture_output=True, text=True, cwd=ROOT, env=env)
    
    # Print output
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode == 0:
        results.add_pass("Offline query contracts", 
                        "All query contract tests passed")
    else:
        results.add_fail("Offline query contracts", 
                        f"Query contract tests failed (exit code {result.returncode})")

def test_no_network_calls(results):
    """Verify that offline.ts doesn't make network API calls."""
    print("\n--- Testing No Network API Calls ---")
    
    content = OFFLINE_TS.read_text()
    
    # Check that fetch is only used for local /data/archive.json
    if "fetch('/data/archive.json')" in content or 'fetch("/data/archive.json")' in content:
        results.add_pass("No network calls", 
                        "Only local fetch to /data/archive.json")
    else:
        results.add_warning("No network calls", 
                          "Could not verify fetch usage pattern")
    
    # Check that there's no REACT_APP_BACKEND_URL usage
    if 'REACT_APP_BACKEND_URL' in content:
        results.add_fail("No network calls", 
                        "References REACT_APP_BACKEND_URL (should not make network calls)")
    else:
        results.add_pass("No backend URL", 
                        "Does not reference REACT_APP_BACKEND_URL")

def test_read_only_enforcement(results):
    """Verify that offline.ts enforces read-only operations."""
    print("\n--- Testing Read-Only Enforcement ---")
    
    content = OFFLINE_TS.read_text()
    
    # Check for method validation
    if "method || 'GET'" in content and "toUpperCase() !== 'GET'" in content:
        results.add_pass("Read-only enforcement", 
                        "Validates that only GET requests are allowed")
    else:
        results.add_fail("Read-only enforcement", 
                        "Missing GET method validation")
    
    # Check for auth/editorial rejection
    if "'/auth'" in content and "'/editorial'" in content:
        results.add_pass("Auth/editorial rejection", 
                        "Rejects auth and editorial endpoints")
    else:
        results.add_fail("Auth/editorial rejection", 
                        "Missing auth/editorial endpoint rejection")

def test_abort_signal_support(results):
    """Verify that offline.ts supports AbortSignal."""
    print("\n--- Testing AbortSignal Support ---")
    
    content = OFFLINE_TS.read_text()
    
    if 'signal?.aborted' in content and 'AbortError' in content:
        results.add_pass("AbortSignal support", 
                        "Implements AbortSignal checking")
    else:
        results.add_fail("AbortSignal support", 
                        "Missing AbortSignal implementation")

def main():
    results = TestResults()
    
    print("="*80)
    print("OFFLINE QUERY CONTRACT TESTS")
    print("="*80)
    
    # Run static analysis tests first
    test_no_network_calls(results)
    test_read_only_enforcement(results)
    test_abort_signal_support(results)
    
    # Run dynamic query tests
    test_offline_query_contracts(results)
    
    # Print summary
    success = results.summary()
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
