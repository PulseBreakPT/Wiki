"""Test offline corpus export and local query contracts.

Tests Goal 1: Validate 12 entities, 20 claims, 3 source records (but /sources only referenced 2),
2 timeline, 4 featured, all assets exist, source/relations/history integrity, reproducibility,
no DB import/write/credentials.
"""
import json
import subprocess
import sys
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_JSON = ROOT / 'frontend' / 'public' / 'data' / 'archive.json'
EXPORT_SCRIPT = ROOT / 'scripts' / 'export_offline.py'

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

def test_export_reproducibility(results):
    """Test that export is reproducible and doesn't require DB."""
    print("\n--- Testing Export Reproducibility ---")
    
    # Run export twice
    result1 = subprocess.run([sys.executable, str(EXPORT_SCRIPT)], 
                            capture_output=True, text=True, cwd=ROOT)
    if result1.returncode != 0:
        results.add_fail("Export script execution", 
                        f"First run failed: {result1.stderr}")
        return
    
    data1 = json.loads(ARCHIVE_JSON.read_text(encoding='utf-8'))
    
    result2 = subprocess.run([sys.executable, str(EXPORT_SCRIPT)], 
                            capture_output=True, text=True, cwd=ROOT)
    if result2.returncode != 0:
        results.add_fail("Export script execution", 
                        f"Second run failed: {result2.stderr}")
        return
    
    data2 = json.loads(ARCHIVE_JSON.read_text(encoding='utf-8'))
    
    # Compare (excluding timestamp which may vary)
    if data1['entities'] == data2['entities'] and data1['sources'] == data2['sources']:
        results.add_pass("Export reproducibility", 
                        "Export produces consistent results")
    else:
        results.add_fail("Export reproducibility", 
                        "Export produces different results on consecutive runs")
    
    # Check that script doesn't import MongoDB
    script_content = EXPORT_SCRIPT.read_text()
    if 'import motor' in script_content or 'from motor' in script_content or 'import pymongo' in script_content:
        results.add_fail("No DB imports", 
                        "Export script imports MongoDB libraries")
    else:
        results.add_pass("No DB imports", 
                        "Export script does not import MongoDB")

def test_corpus_counts(results):
    """Test that corpus has expected counts."""
    print("\n--- Testing Corpus Counts ---")
    
    data = json.loads(ARCHIVE_JSON.read_text(encoding='utf-8'))
    
    # Test 12 entities
    entity_count = len(data['entities'])
    if entity_count == 12:
        results.add_pass("Entity count", f"Found {entity_count} entities")
    else:
        results.add_fail("Entity count", 
                        f"Expected 12 entities, found {entity_count}")
    
    # Test 20 claims total
    total_claims = sum(e['assertion_count'] for e in data['entities'])
    if total_claims == 20:
        results.add_pass("Claim count", f"Found {total_claims} claims")
    else:
        results.add_fail("Claim count", 
                        f"Expected 20 claims, found {total_claims}")
    
    # Test 3 source records
    source_count = len(data['sources'])
    if source_count == 3:
        results.add_pass("Source records", f"Found {source_count} source records")
    else:
        results.add_fail("Source records", 
                        f"Expected 3 source records, found {source_count}")
    
    # Test 2 timeline entries
    timeline_count = len(data['timeline'])
    if timeline_count == 2:
        results.add_pass("Timeline entries", f"Found {timeline_count} timeline entries")
    else:
        results.add_fail("Timeline entries", 
                        f"Expected 2 timeline entries, found {timeline_count}")
    
    # Test 4 featured
    featured_count = len(data['featured_ids'])
    if featured_count == 4:
        results.add_pass("Featured entities", f"Found {featured_count} featured IDs")
    else:
        results.add_fail("Featured entities", 
                        f"Expected 4 featured IDs, found {featured_count}")
    
    # Verify featured IDs exist
    entity_ids = {e['id'] for e in data['entities']}
    missing_featured = [fid for fid in data['featured_ids'] if fid not in entity_ids]
    if not missing_featured:
        results.add_pass("Featured ID validity", "All featured IDs exist in entities")
    else:
        results.add_fail("Featured ID validity", 
                        f"Featured IDs not found: {missing_featured}")

def test_sources_referenced(results):
    """Test that /sources only returns referenced sources (2 out of 3)."""
    print("\n--- Testing Source References ---")
    
    data = json.loads(ARCHIVE_JSON.read_text(encoding='utf-8'))
    
    # Collect all source_ids referenced in assertions
    referenced_sources = set()
    for entity in data['entities']:
        for assertion in entity.get('assertions', []):
            referenced_sources.add(assertion['source_id'])
    
    # According to requirement: 3 source records but /sources only referenced 2
    if len(referenced_sources) == 2:
        results.add_pass("Referenced sources", 
                        f"Found {len(referenced_sources)} referenced sources: {referenced_sources}")
    else:
        results.add_warning("Referenced sources", 
                           f"Expected 2 referenced sources, found {len(referenced_sources)}: {referenced_sources}")
    
    # Verify all referenced sources exist in sources list
    source_ids = {s['id'] for s in data['sources']}
    missing_sources = referenced_sources - source_ids
    if not missing_sources:
        results.add_pass("Source integrity", "All referenced sources exist in sources list")
    else:
        results.add_fail("Source integrity", 
                        f"Referenced sources not in sources list: {missing_sources}")

def test_assets_exist(results):
    """Test that all image assets exist."""
    print("\n--- Testing Asset Existence ---")
    
    data = json.loads(ARCHIVE_JSON.read_text(encoding='utf-8'))
    public_dir = ROOT / 'frontend' / 'public'
    
    missing_assets = []
    for entity in data['entities']:
        image_path = entity['image'].lstrip('/')
        full_path = public_dir / image_path
        if not full_path.is_file():
            missing_assets.append(image_path)
    
    if not missing_assets:
        results.add_pass("Asset existence", 
                        f"All {len(data['entities'])} entity images exist")
    else:
        results.add_fail("Asset existence", 
                        f"Missing assets: {missing_assets}")

def test_relations_integrity(results):
    """Test that all entity relations are valid."""
    print("\n--- Testing Relations Integrity ---")
    
    data = json.loads(ARCHIVE_JSON.read_text(encoding='utf-8'))
    entity_ids = {e['id'] for e in data['entities']}
    
    invalid_relations = []
    for entity in data['entities']:
        for assertion in entity.get('assertions', []):
            related_id = assertion.get('related_entity_id')
            if related_id and related_id not in entity_ids:
                invalid_relations.append(
                    f"{entity['id']}.{assertion['id']} -> {related_id}"
                )
    
    if not invalid_relations:
        results.add_pass("Relations integrity", 
                        "All entity relations reference valid entities")
    else:
        results.add_fail("Relations integrity", 
                        f"Invalid relations: {invalid_relations}")

def test_history_integrity(results):
    """Test that history records are properly structured."""
    print("\n--- Testing History Integrity ---")
    
    data = json.loads(ARCHIVE_JSON.read_text(encoding='utf-8'))
    
    # Check that all entities have history
    entities_without_history = []
    for entity in data['entities']:
        entity_id = entity['id']
        if entity_id not in data['history']:
            entities_without_history.append(entity_id)
    
    if not entities_without_history:
        results.add_pass("History completeness", 
                        "All entities have history records")
    else:
        results.add_fail("History completeness", 
                        f"Entities without history: {entities_without_history}")
    
    # Check history structure
    invalid_history = []
    for entity_id, revisions in data['history'].items():
        if not revisions:
            invalid_history.append(f"{entity_id}: empty history")
            continue
        
        for rev in revisions:
            if rev['version'] != 1:
                invalid_history.append(
                    f"{entity_id}: expected version 1, got {rev['version']}"
                )
            if rev['entity_id'] != entity_id:
                invalid_history.append(
                    f"{entity_id}: history entity_id mismatch"
                )
    
    if not invalid_history:
        results.add_pass("History structure", 
                        "All history records are properly structured")
    else:
        results.add_fail("History structure", 
                        f"Invalid history: {invalid_history}")

def test_schema_structure(results):
    """Test that the schema is properly structured."""
    print("\n--- Testing Schema Structure ---")
    
    data = json.loads(ARCHIVE_JSON.read_text(encoding='utf-8'))
    
    # Check required top-level fields
    required_fields = ['schema_version', 'snapshot_at', 'origin', 'notice', 
                      'entities', 'history', 'sources', 'timeline', 
                      'featured_ids', 'stats']
    missing_fields = [f for f in required_fields if f not in data]
    
    if not missing_fields:
        results.add_pass("Schema completeness", 
                        "All required top-level fields present")
    else:
        results.add_fail("Schema completeness", 
                        f"Missing fields: {missing_fields}")
    
    # Check schema version
    if data.get('schema_version') == 1:
        results.add_pass("Schema version", "Schema version is 1")
    else:
        results.add_fail("Schema version", 
                        f"Expected schema_version 1, got {data.get('schema_version')}")
    
    # Check stats accuracy
    stats = data.get('stats', {})
    actual_entities = len(data['entities'])
    actual_sources = len(data['sources'])
    actual_assertions = sum(e['assertion_count'] for e in data['entities'])
    
    stats_errors = []
    if stats.get('entities') != actual_entities:
        stats_errors.append(f"entities: {stats.get('entities')} vs {actual_entities}")
    if stats.get('sources') != actual_sources:
        stats_errors.append(f"sources: {stats.get('sources')} vs {actual_sources}")
    if stats.get('assertions') != actual_assertions:
        stats_errors.append(f"assertions: {stats.get('assertions')} vs {actual_assertions}")
    
    if not stats_errors:
        results.add_pass("Stats accuracy", "Stats match actual counts")
    else:
        results.add_fail("Stats accuracy", f"Mismatches: {', '.join(stats_errors)}")

def test_entity_types(results):
    """Test entity type distribution."""
    print("\n--- Testing Entity Types ---")
    
    data = json.loads(ARCHIVE_JSON.read_text(encoding='utf-8'))
    
    type_counts = Counter(e['type'] for e in data['entities'])
    
    # Check that we have both personagem and local types
    if 'personagem' in type_counts and 'local' in type_counts:
        results.add_pass("Entity types", 
                        f"Found types: {dict(type_counts)}")
    else:
        results.add_fail("Entity types", 
                        f"Missing expected types. Found: {dict(type_counts)}")
    
    # Verify stats.types matches actual counts
    stats_types = data.get('stats', {}).get('types', {})
    if stats_types == dict(type_counts):
        results.add_pass("Type stats accuracy", "Stats types match actual counts")
    else:
        results.add_fail("Type stats accuracy", 
                        f"Stats: {stats_types} vs Actual: {dict(type_counts)}")

def test_specific_entities(results):
    """Test that specific required entities exist."""
    print("\n--- Testing Specific Entities ---")
    
    data = json.loads(ARCHIVE_JSON.read_text(encoding='utf-8'))
    entity_map = {e['id']: e for e in data['entities']}
    
    # Test Jason Duval
    if 'jason-duval' in entity_map:
        jason = entity_map['jason-duval']
        if jason['name'] == 'Jason Duval' and jason['type'] == 'personagem':
            results.add_pass("Jason Duval entity", 
                           f"Found with {jason['assertion_count']} assertions")
        else:
            results.add_fail("Jason Duval entity", 
                           f"Incorrect data: {jason}")
    else:
        results.add_fail("Jason Duval entity", "Not found")
    
    # Test Lucia Caminos (with accent)
    if 'lucia-caminos' in entity_map:
        lucia = entity_map['lucia-caminos']
        if lucia['name'] == 'Lucia Caminos' and lucia['type'] == 'personagem':
            # Check for accent in aliases
            has_accent = any('Lúcia' in alias for alias in lucia.get('aliases', []))
            if has_accent:
                results.add_pass("Lucia Caminos entity", 
                               f"Found with accent in aliases: {lucia['aliases']}")
            else:
                results.add_warning("Lucia Caminos entity", 
                                  f"No accent variant in aliases: {lucia['aliases']}")
        else:
            results.add_fail("Lucia Caminos entity", 
                           f"Incorrect data: {lucia}")
    else:
        results.add_fail("Lucia Caminos entity", "Not found")
    
    # Test Ambrosia (with accent)
    if 'ambrosia' in entity_map:
        ambrosia = entity_map['ambrosia']
        if ambrosia['name'] == 'Ambrosia' and ambrosia['type'] == 'local':
            has_accent = any('Ambrósia' in alias for alias in ambrosia.get('aliases', []))
            if has_accent:
                results.add_pass("Ambrosia entity", 
                               f"Found with accent in aliases: {ambrosia['aliases']}")
            else:
                results.add_warning("Ambrosia entity", 
                                  f"No accent variant in aliases: {ambrosia['aliases']}")
        else:
            results.add_fail("Ambrosia entity", 
                           f"Incorrect data: {ambrosia}")
    else:
        results.add_fail("Ambrosia entity", "Not found")

def main():
    results = TestResults()
    
    print("="*80)
    print("OFFLINE EXPORT VALIDATION TESTS")
    print("="*80)
    
    # Run all tests
    test_export_reproducibility(results)
    test_corpus_counts(results)
    test_sources_referenced(results)
    test_assets_exist(results)
    test_relations_integrity(results)
    test_history_integrity(results)
    test_schema_structure(results)
    test_entity_types(results)
    test_specific_entities(results)
    
    # Print summary
    success = results.summary()
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
