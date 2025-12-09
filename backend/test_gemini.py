"""Quick test script to verify Gemini AI is working"""
import requests

print("\n" + "="*60)
print("TESTING GEMINI AI INTEGRATION")
print("="*60)

# Test data - phishing URL
data = {
    'type': 'url',
    'content': 'http://fake-sbi-verify.tk/urgent-login',
    'description': 'Suspicious banking URL'
}

print("\n📤 Sending test request to backend...")
try:
    response = requests.post('http://localhost:8000/api/incidents', data=data, timeout=30)
    result = response.json()
    
    print("\n✅ Response received!")
    print(f"   Incident ID: {result.get('incident_id')}")
    print(f"   Risk Score: {result.get('risk_score')}/100")
    print(f"   Severity: {result.get('severity')}")
    
    # Check if Gemini AI was used
    if result.get('ai_powered'):
        print(f"\n🎉 GEMINI AI ACTIVE!")
        print(f"   Model: {result.get('model', 'Unknown')}")
        print(f"   Summary: {result.get('summary', '')[:100]}...")
        
        if result.get('nlp_analysis'):
            print(f"\n🔍 NLP Analysis: WORKING")
            
        if result.get('detailed_description'):
            print(f"\n📝 Detailed Analysis:")
            print(f"   {result.get('detailed_description')[:150]}...")
    else:
        print(f"\n⚠️  USING FALLBACK (Rule-based)")
        print(f"   Reason: {result.get('fallback_reason', 'Unknown')}")
        print(f"   Model: {result.get('model', 'Unknown')}")
        
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "="*60)
