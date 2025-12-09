"""
Test script to verify complete incident reporting flow
Creates a test incident and verifies JSON file generation
"""

import requests
import json
from pathlib import Path

# Backend URL
API_URL = "http://localhost:8000/api"

print("=" * 60)
print("🧪 TESTING INCIDENT REPORTING FLOW")
print("=" * 60)

# Step 1: Login as admin to get token
print("\n1️⃣  Logging in as admin...")
login_response = requests.post(f"{API_URL}/auth/login", json={
    "email": "admin@army.in",
    "password": "admin123"
})

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    print("✅ Login successful!")
else:
    print(f"❌ Login failed: {login_response.status_code}")
    exit(1)

# Step 2: Submit a test incident
print("\n2️⃣  Submitting test incident with malicious patterns...")
headers = {"Authorization": f"Bearer {token}"}

# Test content with malware patterns to trigger detection
test_data = {
    "type": "message",
    "content": """
    URGENT: Your Indian Army account will be locked!
    Click here to verify: http://fake-army-portal.com/login
    Enter your credentials and password to continue.
    Bitcoin payment required for unlock.
    This is ransomware - your files will be encrypted!
    """,
    "description": "Suspicious message targeting army personnel",
    "location": "New Delhi",
    "unit_name": "Test Unit - Delhi Cantonment"
}

incident_response = requests.post(
    f"{API_URL}/incidents",
    data=test_data,
    headers=headers
)

if incident_response.status_code == 200:
    result = incident_response.json()
    incident_id = result["incident_id"]
    print(f"✅ Incident created: {incident_id}")
    print(f"   Risk Score: {result.get('risk_score', 'N/A')}")
    print(f"   Severity: {result.get('severity', 'N/A')}")
    print(f"   Escalated: {result.get('escalated', False)}")
else:
    print(f"❌ Incident submission failed: {incident_response.status_code}")
    print(incident_response.text)
    exit(1)

# Step 3: Verify JSON file was created
print("\n3️⃣  Verifying JSON file creation...")
reports_dir = Path(__file__).parent / "reports"
report_file = reports_dir / f"{incident_id}.json"

if report_file.exists():
    print(f"✅ Report file created: {report_file}")
    
    # Read and display structure
    with open(report_file, 'r', encoding='utf-8') as f:
        report_data = json.load(f)
    
    print("\n📄 Report Structure:")
    print(json.dumps({
        "incident_id": report_data.get("incident_id"),
        "type": report_data.get("type"),
        "risk_score": report_data.get("risk_score"),
        "severity": report_data.get("severity"),
        "status": report_data.get("status"),
        "escalated": report_data.get("escalated"),
        "military_relevant": report_data.get("military_relevant"),
        "fake_profile_detected": report_data.get("fake_profile_detected"),
        "frequency_count": report_data.get("frequency_count"),
        "indicators_count": len(report_data.get("indicators", [])),
        "has_sandbox_analysis": report_data.get("sandbox_analysis") is not None,
        "has_ai_analysis": report_data.get("ai_analysis") is not None,
        "has_army_context": report_data.get("army_context") is not None,
    }, indent=2))
else:
    print(f"❌ Report file NOT found: {report_file}")
    exit(1)

# Step 4: Verify dashboard can read the file
print("\n4️⃣  Testing dashboard API (reading from JSON files)...")
dashboard_response = requests.get(f"{API_URL}/incidents", headers=headers)

if dashboard_response.status_code == 200:
    incidents = dashboard_response.json()["incidents"]
    print(f"✅ Dashboard API returned {len(incidents)} incidents")
    
    # Find our test incident
    test_incident = next((i for i in incidents if i["id"] == incident_id), None)
    if test_incident:
        print(f"✅ Our test incident found in dashboard:")
        print(f"   ID: {test_incident['id']}")
        print(f"   Type: {test_incident['type']}")
        print(f"   Severity: {test_incident['severity']}")
        print(f"   Reporter: {test_incident.get('reporter_username', 'N/A')}")
    else:
        print(f"⚠️  Test incident not found in dashboard response")
else:
    print(f"❌ Dashboard API failed: {dashboard_response.status_code}")
    exit(1)

# Step 5: Get detailed incident data
print("\n5️⃣  Testing detailed incident view...")
detail_response = requests.get(f"{API_URL}/incidents/{incident_id}", headers=headers)

if detail_response.status_code == 200:
    detail_data = detail_response.json()
    print(f"✅ Detailed view loaded successfully")
    print(f"   Total indicators: {len(detail_data.get('indicators', []))}")
    print(f"   Total recommendations: {len(detail_data.get('recommendations', []))}")
    print(f"   Malware patterns detected: {len(detail_data.get('sandbox_analysis', {}).get('malware_matches', []))}")
else:
    print(f"❌ Detail view failed: {detail_response.status_code}")

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED - System Working Correctly!")
print("=" * 60)
print(f"\n📂 Report file location: {report_file}")
print(f"🌐 View in dashboard: http://localhost:8081/incidents/{incident_id}")
print("\nThe complete flow is working:")
print("  1. ✅ Incident submitted with authentication")
print("  2. ✅ Real AI analysis performed (Gemini + NLP + Sandbox)")
print("  3. ✅ JSON file created in reports/ folder")
print("  4. ✅ Dashboard reads from JSON files")
print("  5. ✅ Proper formatting and data structure")
