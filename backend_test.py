#!/usr/bin/env python3
"""
VI Archive Backend API Smoke Test
Tests public API endpoints for non-regression verification
"""
import requests
import sys
import json
from typing import Dict, Any

# Backend URL from frontend/.env
BASE_URL = "https://android-release-auto.preview.emergentagent.com"

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        
    def add_pass(self, test_name: str):
        self.passed += 1
        print(f"✅ PASS: {test_name}")
        
    def add_fail(self, test_name: str, reason: str):
        self.failed += 1
        error_msg = f"❌ FAIL: {test_name} - {reason}"
        self.errors.append(error_msg)
        print(error_msg)
        
    def summary(self):
        print("\n" + "="*80)
        print(f"TEST SUMMARY: {self.passed} passed, {self.failed} failed")
        print("="*80)
        if self.errors:
            print("\nFAILED TESTS:")
            for error in self.errors:
                print(f"  {error}")
        return self.failed == 0

results = TestResults()

def test_health():
    """Test /api/health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok" and data.get("service") == "VI Archive":
                results.add_pass("Health endpoint")
                return True
            else:
                results.add_fail("Health endpoint", f"Unexpected response: {data}")
                return False
        else:
            results.add_fail("Health endpoint", f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        results.add_fail("Health endpoint", f"Exception: {str(e)}")
        return False

def test_stats():
    """Test /api/v1/stats endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/stats", timeout=10)
        if response.status_code == 200:
            data = response.json()
            required_fields = ['entities', 'sources', 'assertions', 'types']
            missing = [f for f in required_fields if f not in data]
            if missing:
                results.add_fail("Stats endpoint", f"Missing fields: {missing}")
                return False
            
            # Verify counts are reasonable
            if data['entities'] > 0 and data['sources'] > 0:
                results.add_pass(f"Stats endpoint (entities: {data['entities']}, sources: {data['sources']}, assertions: {data['assertions']})")
                return True
            else:
                results.add_fail("Stats endpoint", f"Zero counts: {data}")
                return False
        else:
            results.add_fail("Stats endpoint", f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        results.add_fail("Stats endpoint", f"Exception: {str(e)}")
        return False

def test_featured():
    """Test /api/v1/featured endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/featured", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                # Check for expected featured entities
                entity_ids = [e.get('id') for e in data]
                expected = ['jason-duval', 'lucia-caminos']
                found = [eid for eid in expected if eid in entity_ids]
                
                if len(found) >= 2:
                    results.add_pass(f"Featured endpoint ({len(data)} entities, includes {', '.join(found)})")
                    return True
                else:
                    results.add_fail("Featured endpoint", f"Expected entities not found. Got: {entity_ids}")
                    return False
            else:
                results.add_fail("Featured endpoint", f"Empty or invalid response: {data}")
                return False
        else:
            results.add_fail("Featured endpoint", f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        results.add_fail("Featured endpoint", f"Exception: {str(e)}")
        return False

def test_entities_list():
    """Test /api/v1/entities endpoint (pagination, basic list)"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/entities", timeout=10)
        if response.status_code == 200:
            data = response.json()
            required_fields = ['items', 'total']
            missing = [f for f in required_fields if f not in data]
            if missing:
                results.add_fail("Entities list", f"Missing fields: {missing}")
                return False
            
            if isinstance(data['items'], list) and data['total'] > 0:
                results.add_pass(f"Entities list (total: {data['total']}, returned: {len(data['items'])})")
                return True
            else:
                results.add_fail("Entities list", f"No entities found: {data}")
                return False
        else:
            results.add_fail("Entities list", f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        results.add_fail("Entities list", f"Exception: {str(e)}")
        return False

def test_entities_search():
    """Test /api/v1/entities with search query"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/entities?q=jason", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data['items'], list):
                results.add_pass(f"Entities search (q=jason, found: {len(data['items'])})")
                return True
            else:
                results.add_fail("Entities search", f"Invalid items: {data}")
                return False
        else:
            results.add_fail("Entities search", f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        results.add_fail("Entities search", f"Exception: {str(e)}")
        return False

def test_entities_filter_type():
    """Test /api/v1/entities with type filter"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/entities?type=person", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data['items'], list):
                results.add_pass(f"Entities filter by type (type=person, found: {len(data['items'])})")
                return True
            else:
                results.add_fail("Entities filter by type", f"Invalid items: {data}")
                return False
        else:
            results.add_fail("Entities filter by type", f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        results.add_fail("Entities filter by type", f"Exception: {str(e)}")
        return False

def test_entities_pagination():
    """Test /api/v1/entities with limit and cursor"""
    try:
        # First page
        response = requests.get(f"{BASE_URL}/api/v1/entities?limit=2", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if len(data['items']) > 0:
                cursor = data.get('next_cursor')
                if cursor:
                    # Second page
                    response2 = requests.get(f"{BASE_URL}/api/v1/entities?limit=2&cursor={cursor}", timeout=10)
                    if response2.status_code == 200:
                        data2 = response2.json()
                        results.add_pass(f"Entities pagination (page1: {len(data['items'])}, page2: {len(data2['items'])})")
                        return True
                    else:
                        results.add_fail("Entities pagination", f"Page 2 failed: {response2.status_code}")
                        return False
                else:
                    results.add_pass("Entities pagination (single page, no cursor)")
                    return True
            else:
                results.add_fail("Entities pagination", "No items returned")
                return False
        else:
            results.add_fail("Entities pagination", f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        results.add_fail("Entities pagination", f"Exception: {str(e)}")
        return False

def test_entity_detail(slug: str, entity_name: str):
    """Test /api/v1/entities/{slug} endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/entities/{slug}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            required_fields = ['id', 'name', 'type', 'assertions']
            missing = [f for f in required_fields if f not in data]
            if missing:
                results.add_fail(f"Entity detail ({entity_name})", f"Missing fields: {missing}")
                return False
            
            # Check if assertions have source data
            assertions = data.get('assertions', [])
            has_sources = all('source' in a for a in assertions)
            
            results.add_pass(f"Entity detail ({entity_name}, {len(assertions)} assertions, sources: {has_sources})")
            return True
        elif response.status_code == 404:
            results.add_fail(f"Entity detail ({entity_name})", f"Entity not found (404)")
            return False
        else:
            results.add_fail(f"Entity detail ({entity_name})", f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        results.add_fail(f"Entity detail ({entity_name})", f"Exception: {str(e)}")
        return False

def test_entity_history(slug: str, entity_name: str):
    """Test /api/v1/entities/{slug}/history endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/entities/{slug}/history", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                results.add_pass(f"Entity history ({entity_name}, {len(data)} versions)")
                return True
            else:
                results.add_fail(f"Entity history ({entity_name})", f"Invalid response: {data}")
                return False
        elif response.status_code == 404:
            results.add_fail(f"Entity history ({entity_name})", f"Entity not found (404)")
            return False
        else:
            results.add_fail(f"Entity history ({entity_name})", f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        results.add_fail(f"Entity history ({entity_name})", f"Exception: {str(e)}")
        return False

def test_sources():
    """Test /api/v1/sources endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/sources", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                # Check source structure
                first_source = data[0]
                required_fields = ['id', 'title']
                missing = [f for f in required_fields if f not in first_source]
                if missing:
                    results.add_fail("Sources endpoint", f"Missing fields in source: {missing}")
                    return False
                
                results.add_pass(f"Sources endpoint ({len(data)} sources)")
                return True
            else:
                results.add_fail("Sources endpoint", f"No sources found: {data}")
                return False
        else:
            results.add_fail("Sources endpoint", f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        results.add_fail("Sources endpoint", f"Exception: {str(e)}")
        return False

def test_timeline():
    """Test /api/v1/timeline endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/timeline", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                results.add_pass(f"Timeline endpoint ({len(data)} entries)")
                return True
            else:
                results.add_fail("Timeline endpoint", f"Invalid response: {data}")
                return False
        else:
            results.add_fail("Timeline endpoint", f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        results.add_fail("Timeline endpoint", f"Exception: {str(e)}")
        return False

def test_auth_me_unauthenticated():
    """Test /api/v1/auth/me rejects unauthenticated requests"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/auth/me", timeout=10)
        if response.status_code == 401:
            results.add_pass("Auth /me rejection (unauthenticated)")
            return True
        else:
            results.add_fail("Auth /me rejection", f"Expected 401, got {response.status_code}: {response.text}")
            return False
    except Exception as e:
        results.add_fail("Auth /me rejection", f"Exception: {str(e)}")
        return False

def main():
    print("="*80)
    print("VI ARCHIVE BACKEND API SMOKE TEST")
    print("="*80)
    print(f"Testing backend: {BASE_URL}")
    print("="*80 + "\n")
    
    # Run all tests
    print("1. Testing health endpoint...")
    test_health()
    
    print("\n2. Testing stats endpoint...")
    test_stats()
    
    print("\n3. Testing featured endpoint...")
    test_featured()
    
    print("\n4. Testing entities list endpoint...")
    test_entities_list()
    
    print("\n5. Testing entities search...")
    test_entities_search()
    
    print("\n6. Testing entities filter by type...")
    test_entities_filter_type()
    
    print("\n7. Testing entities pagination...")
    test_entities_pagination()
    
    print("\n8. Testing entity detail (jason-duval)...")
    test_entity_detail("jason-duval", "Jason Duval")
    
    print("\n9. Testing entity detail (lucia-caminos)...")
    test_entity_detail("lucia-caminos", "Lucia Caminos")
    
    print("\n10. Testing entity history (jason-duval)...")
    test_entity_history("jason-duval", "Jason Duval")
    
    print("\n11. Testing entity history (lucia-caminos)...")
    test_entity_history("lucia-caminos", "Lucia Caminos")
    
    print("\n12. Testing sources endpoint...")
    test_sources()
    
    print("\n13. Testing timeline endpoint...")
    test_timeline()
    
    print("\n14. Testing auth/me rejection (unauthenticated)...")
    test_auth_me_unauthenticated()
    
    # Print summary
    success = results.summary()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
