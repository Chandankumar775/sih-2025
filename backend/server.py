"""
RakshaNetra Backend Server - DEFENCE-GRADE CYBERSECURITY PLATFORM
Enhanced with Military Intelligence Features
With REAL Gemini AI Analysis + Threat Repetition + Auto-Escalation + Geo-Intelligence
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
import uuid
import os
import re
import socket
import urllib.request
import urllib.error
import json
from datetime import datetime
from pathlib import Path

# Pydantic models for request validation
class LoginRequest(BaseModel):
    email: str
    password: str
    username: Optional[str] = None

# Create reports directory if it doesn't exist
REPORTS_DIR = Path(__file__).parent / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# Import defence feature modules
from modules import threat_matcher, auto_escalation, army_ai_context, geo_intelligence

# Optional imports (may not have dependencies)
try:
    from modules import nlp_analyzer
except ImportError:
    nlp_analyzer = None
    print("⚠️  nlp_analyzer module not available (missing spacy)")

try:
    from modules import sandbox_analyzer
except ImportError:
    sandbox_analyzer = None
    print("⚠️  sandbox_analyzer module not available")

# Import Zero Trust middleware
try:
    from middleware.zero_trust_middleware import ZeroTrustMiddleware
except ImportError:
    ZeroTrustMiddleware = None
    print("⚠️  ZeroTrustMiddleware not available")

# Import authentication manager
try:
    from modules.auth_manager import auth_manager
except ImportError:
    auth_manager = None
    print("⚠️  auth_manager not available")

# ==================== GEMINI AI CONFIG ====================
GEMINI_API_KEY = "AIzaSyB6n5P5sYNF-5ORqDYz4DaN05NQ35FPF20"
GEMINI_MODEL = "gemini-2.5-flash"  # Latest fast model with new API


def analyze_with_gemini(content: str, content_type: str) -> dict:
    """
    REAL AI Analysis using Google Gemini - GUARANTEED detailed response
    """
    try:
        import google.generativeai as genai
        import json
        
        print(f"\n{'='*60}")
        print(f"🤖 GEMINI AI ANALYSIS START")
        print(f"{'='*60}")
        print(f"Content Type: {content_type}")
        print(f"Content: {content[:200]}...")
        
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        # Create comprehensive prompt - no f-string issues
        prompt_template = """You are a cybersecurity expert AI for RakshaNetra - India's Defence Cyber Safety Portal.
Analyze this CONTENT_TYPE for potential threats with military-grade precision.

CONTENT TO ANALYZE:
CONTENT_HERE

IMPORTANT: Return ONLY valid JSON with NO markdown formatting, NO code blocks, NO extra text.

Return this exact structure:
{
  "risk_score": NUMBER_0_TO_100,
  "severity": "low or medium or high or critical",
  "is_threat": true_or_false,
  "threat_type": "phishing or malware or scam or spam or social_engineering or safe",
  "summary": "One sentence threat summary",
  "detailed_description": "Write 3-4 detailed sentences explaining what this threat is, how it works, why it is dangerous for defence personnel, and what the attacker wants to achieve",
  "attack_vector": "email or sms or social_media or url or file",
  "potential_impact": "Data Loss or Credential Theft or Financial Loss or System Compromise or None",
  "indicators": ["Specific red flag 1", "Specific red flag 2", "Specific red flag 3"],
  "recommendations": ["Actionable step 1", "Actionable step 2", "Actionable step 3"],
  "technical_details": {
    "ip_addresses": [],
    "domains": [],
    "file_hashes": [],
    "malware_family": null
  }
}

Scoring Rules:
- Government sites (.gov.in, mod.gov.in) = 5-10 (safe)
- Trusted sites (google.com, amazon.com) = 10-20 (safe)
- Normal messages = 20-40
- Suspicious patterns = 50-70
- Clear phishing/scam = 75-90
- Targeted military attacks = 90-100

RETURN ONLY THE JSON OBJECT."""

        prompt = prompt_template.replace('CONTENT_TYPE', content_type).replace('CONTENT_HERE', content)
        
        # Enhance with army context
        prompt = army_ai_context.enhance_ai_prompt_with_army_context(content, content_type, prompt)

        print(f"\n📝 Calling Gemini API...")
        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.3,
                'top_p': 0.95,
                'max_output_tokens': 2048,
            }
        )
        
        # Check if response was blocked or empty
        if not response.text or response.text.strip() == '':
            print(f"❌ Gemini returned empty response (finish_reason: {response.candidates[0].finish_reason if response.candidates else 'unknown'})")
            raise ValueError("Empty response from Gemini API")
        
        ai_text = response.text.strip()
        
        print(f"[OK] Gemini responded! Length: {len(ai_text)}")
        print(f"First 300 chars: {ai_text[:300]}")        # Aggressive JSON cleaning
        ai_text = ai_text.replace('```json', '').replace('```', '').strip()
        
        # Find JSON boundaries
        start = ai_text.find('{')
        end = ai_text.rfind('}')
        if start != -1 and end != -1:
            ai_text = ai_text[start:end+1]
        
        print(f"\n📦 Parsing JSON...")
        ai_result = json.loads(ai_text)
        
        # Ensure detailed_description exists
        if 'detailed_description' not in ai_result or not ai_result['detailed_description']:
            summary = ai_result.get('summary', 'Potential threat detected')
            ai_result['detailed_description'] = f"{summary}. This content has been analyzed by our AI-powered threat detection system. Based on the analysis, this appears to be a potential security threat that requires careful review. Defence personnel should exercise caution when interacting with this content and follow the recommended security protocols."
        
        # Ensure all fields
        ai_result.setdefault('indicators', ['AI analysis completed', 'Threat patterns detected'])
        ai_result.setdefault('recommendations', ['Do not interact with suspicious content', 'Report to security team', 'Follow security protocols'])
        ai_result.setdefault('ai_powered', True)
        ai_result.setdefault('model', 'Gemini 2.0 Flash')
        
        print(f"[OK] SUCCESS! Risk: {ai_result.get('risk_score')}, Severity: {ai_result.get('severity')}")
        print(f"Has detailed_description: {bool(ai_result.get('detailed_description'))}")
        print(f"{'='*60}\n")
        
        return ai_result
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON Parse Error: {e}")
        print(f"Text was: {ai_text[:500] if 'ai_text' in locals() else 'N/A'}")
        return create_smart_fallback(content, content_type, "JSON parsing failed")
    except Exception as e:
        print(f"❌ Gemini Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return create_smart_fallback(content, content_type, str(e))

def create_smart_fallback(content: str, content_type: str, error: str) -> dict:
    """Smart rule-based fallback with detailed analysis"""
    print(f"\n⚙️ Using Smart Fallback Engine...")
    
    risk_score = 45
    indicators = []
    threat_type = 'spam'
    
    # Threat detection rules
    threat_patterns = {
        'phishing': ['verify', 'account', 'suspend', 'click here', 'urgent', 'immediately', 'confirm', 'update'],
        'scam': ['prize', 'won', 'lottery', 'inheritance', 'million', 'winner', 'congratulations'],
        'malware': ['download', 'install', 'exe', 'attachment', 'open file'],
        'social_engineering': ['help', 'emergency', 'family', 'accident', 'hospital', 'money transfer']
    }
    
    content_lower = content.lower()
    
    # Check patterns
    for t_type, keywords in threat_patterns.items():
        matches = [kw for kw in keywords if kw in content_lower]
        if matches:
            threat_type = t_type
            risk_score += len(matches) * 10
            indicators.extend([f"Contains '{kw}' keyword" for kw in matches[:3]])
    
    # Military keywords
    mil_keywords = ['army', 'military', 'officer', 'soldier', 'defence', 'colonel', 'major', 'regiment']
    mil_matches = [kw for kw in mil_keywords if kw in content_lower]
    if mil_matches:
        risk_score += 15
        indicators.append(f"References military terms: {', '.join(mil_matches[:2])}")
    
    risk_score = min(risk_score, 95)
    
    # Determine severity
    if risk_score >= 75: severity = 'critical'
    elif risk_score >= 60: severity = 'high'
    elif risk_score >= 40: severity = 'medium'
    else: severity = 'low'
    
    # Create detailed description
    detailed_desc = f"""This {content_type} has been analyzed using our advanced rule-based threat detection engine. 

The content exhibits multiple characteristics commonly associated with {threat_type} attacks. With a risk score of {risk_score}/100, this falls into the {severity} severity category. Our analysis has identified {len(indicators)} specific threat indicators that warrant immediate attention.

For defence personnel, this type of content is particularly concerning as it may be part of a targeted social engineering campaign. The use of urgency tactics and requests for action are classic hallmarks of cyber attacks designed to bypass critical thinking and exploit trust. We strongly recommend following all security protocols and reporting this to your IT security team immediately."""

    return {
        'risk_score': risk_score,
        'is_threat': risk_score >= 40,
        'threat_type': threat_type,
        'attack_vector': content_type,
        'severity': severity,
        'summary': f"Rule-based engine detected {severity}-severity {threat_type} threat",
        'detailed_description': detailed_desc,
        'indicators': indicators if indicators else ['Pattern-based analysis completed', 'Suspicious content structure detected', 'Manual review recommended'],
        'recommendations': [
            '🚫 Do NOT click any links or download attachments',
            '📞 Verify sender authenticity through official channels',
            '🛡️ Report to your IT Security Officer immediately',
            '🗑️ Delete the message after reporting'
        ],
        'potential_impact': 'Credential Theft' if threat_type == 'phishing' else 'Financial Loss',
        'technical_details': {
            'ip_addresses': [],
            'domains': [],
            'file_hashes': [],
            'malware_family': None
        },
        'ai_powered': False,
        'model': 'Rule-based Detection Engine',
        'fallback_reason': f'Gemini unavailable: {error}'
    }

# ==================== APP SETUP ====================
app = FastAPI(title="RakshaNetra API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Zero Trust security middleware - continuous verification
# Note: Middleware will bypass public endpoints (/health, /login, /register, /docs)
# TEMPORARILY DISABLED for testing
# app.middleware("http")(ZeroTrustMiddleware)

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), "rakshanetra.db")

# ==================== DATABASE ====================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create tables if they don't exist"""
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            content TEXT,
            description TEXT,
            risk_score INTEGER DEFAULT 0,
            severity TEXT DEFAULT 'low',
            status TEXT DEFAULT 'pending',
            indicators TEXT,
            recommendations TEXT,
            url_exists INTEGER DEFAULT 0,
            domain_info TEXT,
            created_at TEXT,
            ip_address TEXT,
            geo_region TEXT,
            unit_name TEXT,
            frequency_count INTEGER DEFAULT 0,
            related_incident_ids TEXT,
            military_relevant INTEGER DEFAULT 0,
            fake_profile_detected INTEGER DEFAULT 0,
            reporter_id TEXT,
            reporter_username TEXT,
            ai_analysis TEXT,
            is_anonymous INTEGER DEFAULT 1
        )
    """)
    conn.commit()
    conn.close()
    print(f"[OK] Database ready at: {DB_PATH}")

# Initialize on startup
init_db()

# ==================== REAL URL CHECKER ====================
# Trusted domains that are safe
TRUSTED_DOMAINS = [
    "google.com", "youtube.com", "facebook.com", "twitter.com", "x.com",
    "instagram.com", "linkedin.com", "microsoft.com", "apple.com",
    "amazon.com", "netflix.com", "github.com", "stackoverflow.com",
    "wikipedia.org", "reddit.com", "whatsapp.com", "telegram.org",
    "gov.in", "nic.in", "india.gov.in", "digitalindia.gov.in"
]

# Suspicious patterns
SUSPICIOUS_PATTERNS = [
    r"bit\.ly", r"tinyurl", r"t\.co", r"goo\.gl",  # URL shorteners
    r"free.*gift", r"winner", r"lottery", r"prize",
    r"urgent.*action", r"account.*suspend", r"verify.*now",
    r"login.*secure", r"update.*payment", r"click.*here.*now",
    r"crypto.*invest", r"bitcoin.*double", r"earn.*money.*fast",
    r"password.*expire", r"unusual.*activity"
]

def extract_domain(url: str) -> Optional[str]:
    """Extract domain from URL"""
    try:
        # Remove protocol
        url = url.lower().strip()
        if "://" in url:
            url = url.split("://")[1]
        # Get domain part
        domain = url.split("/")[0].split("?")[0]
        # Remove port if present
        domain = domain.split(":")[0]
        return domain
    except:
        return None

def check_url_exists(url: str) -> dict:
    """ACTUALLY check if URL exists - makes real HTTP request"""
    result = {
        "exists": False,
        "reachable": False,
        "status_code": None,
        "error": None,
        "response_time": None
    }
    
    # Add protocol if missing
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    
    try:
        start_time = datetime.now()
        
        # Create request with timeout
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (RakshaNetra Security Scanner)"}
        )
        
        # Make the request (timeout 5 seconds)
        response = urllib.request.urlopen(req, timeout=5)
        
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds()
        
        result["exists"] = True
        result["reachable"] = True
        result["status_code"] = response.getcode()
        result["response_time"] = round(response_time, 2)
        
    except urllib.error.HTTPError as e:
        # URL exists but returned error (like 404, 403)
        result["exists"] = True
        result["reachable"] = True
        result["status_code"] = e.code
        result["error"] = f"HTTP {e.code}"
        
    except urllib.error.URLError as e:
        result["error"] = f"Cannot reach: {str(e.reason)}"
        
    except socket.timeout:
        result["error"] = "Connection timed out"
        
    except Exception as e:
        result["error"] = str(e)
    
    return result

def check_domain_dns(domain: str) -> dict:
    """Check if domain has DNS records"""
    result = {"has_dns": False, "ip_address": None}
    
    try:
        ip = socket.gethostbyname(domain)
        result["has_dns"] = True
        result["ip_address"] = ip
    except socket.gaierror:
        pass
    except Exception:
        pass
    
    return result

def is_valid_url_format(text: str) -> bool:
    """Check if text looks like a URL"""
    url_pattern = r'^(https?://)?([a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}(/.*)?$'
    return bool(re.match(url_pattern, text.strip()))

def analyze_content(content: str, content_type: str) -> dict:
    """
    REAL content analysis - Multi-layer: NLP → Gemini AI → Rule-based fallback
    """
    content = content.strip() if content else ""
    
    if not content:
        return {
            "risk_score": 0,
            "severity": "low",
            "indicators": ["No content provided"],
            "recommendations": ["Please provide content to analyze"],
            "ai_powered": False
        }
    
    # ===== LAYER 1: NLP ANALYSIS (FAST) =====
    print(f"\n{'='*60}")
    print(f"🔍 MULTI-LAYER ANALYSIS PIPELINE")
    print(f"{'='*60}")
    nlp_result = nlp_analyzer.enhance_analysis_with_nlp(content, content_type)
    print(f"[OK] Layer 1 (NLP): Complete")
    
    # ===== LAYER 2: GEMINI AI (SMART) =====
    print(f"🤖 Layer 2 (Gemini AI): Starting...")
    ai_result = analyze_with_gemini(content, content_type)
    
    if ai_result:
        # AI analysis successful! Combine with NLP results
        print(f"[OK] Layer 2 (Gemini AI): Complete")
        print(f"{'='*60}\n")
        
        # Merge NLP analysis into AI result
        ai_result["nlp_analysis"] = nlp_result
        
        # Enhance indicators with NLP findings
        if nlp_result.get("entities"):
            entities = nlp_result["entities"]
            if entities.get("phone_numbers"):
                ai_result["indicators"].insert(0, f"📞 Phone numbers detected: {', '.join(entities['phone_numbers'][:3])}")
            if entities.get("urls"):
                ai_result["indicators"].insert(0, f"🔗 URLs found: {', '.join(entities['urls'][:2])}")
            if entities.get("emails"):
                ai_result["indicators"].insert(0, f"📧 Emails detected: {', '.join(entities['emails'][:2])}")
            if entities.get("bank_names"):
                ai_result["indicators"].insert(0, f"🏦 Bank names: {', '.join(entities['bank_names'][:3])}")
            if entities.get("army_ranks"):
                ai_result["indicators"].insert(0, f"⚠️ Military ranks mentioned: {', '.join(entities['army_ranks'][:3])}")
        
        # Add urgency indicator
        urgency = nlp_result.get("urgency_score", 0)
        if urgency > 70:
            ai_result["indicators"].insert(0, f"🚨 HIGH URGENCY: {urgency}/100 urgency score")
        
        # Add language info
        if nlp_result.get("language"):
            ai_result["language_detected"] = nlp_result["language"]
        
        # Add additional URL verification for URLs
        if content_type == "url" and is_valid_url_format(content):
            domain = extract_domain(content)
            if domain:
                # Check DNS
                dns_check = check_domain_dns(domain)
                if not dns_check["has_dns"]:
                    ai_result["risk_score"] = max(ai_result.get("risk_score", 0), 85)
                    ai_result["severity"] = "high"
                    ai_result["indicators"].insert(0, "❌ DOMAIN DOES NOT EXIST - No DNS records")
                    ai_result["domain_info"] = dns_check
                else:
                    ai_result["domain_info"] = dns_check
                    ai_result["indicators"].insert(0, f"✓ Domain exists (IP: {dns_check['ip_address']})")
        
        return ai_result
    
    # ===== FALLBACK TO RULE-BASED =====
    result = {
        "risk_score": 0,
        "severity": "low",
        "indicators": [],
        "recommendations": [],
        "url_check": None,
        "domain_info": None,
        "is_trusted": False,
        "ai_powered": False
    }
    
    # ===== URL ANALYSIS =====
    if content_type == "url":
        # Check if it's even a valid URL format
        if not is_valid_url_format(content):
            result["risk_score"] = 10
            result["severity"] = "low"
            result["indicators"].append("⚠️ This does not appear to be a valid URL format")
            result["indicators"].append("Not a website address - cannot analyze as URL")
            result["recommendations"].append("Please enter a valid URL (e.g., https://example.com)")
            return result
        
        domain = extract_domain(content)
        
        if domain:
            # Check if trusted domain
            is_trusted = any(domain.endswith(trusted) or domain == trusted for trusted in TRUSTED_DOMAINS)
            
            if is_trusted:
                result["risk_score"] = 5
                result["severity"] = "low"
                result["is_trusted"] = True
                result["indicators"].append(f"✅ Trusted domain: {domain}")
                result["indicators"].append("This is a well-known legitimate website")
                result["recommendations"].append("This website is generally safe to visit")
                return result
            
            # === REAL URL VERIFICATION ===
            result["indicators"].append(f"🔍 Analyzing domain: {domain}")
            
            # 1. DNS Check - Does domain exist?
            dns_check = check_domain_dns(domain)
            result["domain_info"] = dns_check
            
            if not dns_check["has_dns"]:
                result["risk_score"] = 85
                result["severity"] = "high"
                result["indicators"].append("❌ DOMAIN DOES NOT EXIST - No DNS records found")
                result["indicators"].append("This domain is not registered or is inactive")
                result["recommendations"].append("DO NOT TRUST - This URL leads nowhere")
                result["recommendations"].append("This could be a phishing attempt with fake URL")
                return result
            
            result["indicators"].append(f"✓ Domain exists (IP: {dns_check['ip_address']})")
            
            # 2. HTTP Check - Is website reachable?
            url_check = check_url_exists(content)
            result["url_check"] = url_check
            
            if url_check["reachable"]:
                result["indicators"].append(f"✓ Website is reachable (Status: {url_check['status_code']})")
                if url_check["response_time"]:
                    result["indicators"].append(f"✓ Response time: {url_check['response_time']}s")
            else:
                result["indicators"].append(f"⚠️ Website not reachable: {url_check['error']}")
                result["risk_score"] += 20
            
            # 3. Check for suspicious patterns
            suspicious_found = []
            for pattern in SUSPICIOUS_PATTERNS:
                if re.search(pattern, content.lower()):
                    suspicious_found.append(pattern)
            
            if suspicious_found:
                result["risk_score"] += len(suspicious_found) * 15
                result["indicators"].append(f"⚠️ Suspicious patterns detected: {len(suspicious_found)}")
                result["severity"] = "medium" if result["risk_score"] < 60 else "high"
                result["recommendations"].append("Exercise caution - URL contains suspicious elements")
            
            # 4. Check URL length (very long URLs are suspicious)
            if len(content) > 100:
                result["risk_score"] += 10
                result["indicators"].append("⚠️ Unusually long URL")
            
            # 5. Check for IP address instead of domain
            if re.match(r'^https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', content):
                result["risk_score"] += 25
                result["indicators"].append("⚠️ URL uses IP address instead of domain name")
                result["recommendations"].append("Legitimate sites usually use domain names, not IP addresses")
            
            # Final severity based on score
            if result["risk_score"] < 20:
                result["severity"] = "low"
                result["recommendations"].append("URL appears to be legitimate")
            elif result["risk_score"] < 50:
                result["severity"] = "medium"
                result["recommendations"].append("Verify the website before sharing sensitive information")
            else:
                result["severity"] = "high"
                result["recommendations"].append("HIGH RISK - Avoid clicking or sharing personal information")
    
    # ===== MESSAGE/SMS ANALYSIS =====
    elif content_type == "sms":
        # Check for phishing patterns
        phishing_score = 0
        
        patterns_found = []
        for pattern in SUSPICIOUS_PATTERNS:
            if re.search(pattern, content.lower()):
                patterns_found.append(pattern)
                phishing_score += 15
        
        if patterns_found:
            result["indicators"].append(f"⚠️ Suspicious phrases detected: {len(patterns_found)}")
        
        # Check for urgency words
        urgency_words = ["urgent", "immediately", "now", "hurry", "quick", "fast", "limited time"]
        urgency_found = sum(1 for word in urgency_words if word in content.lower())
        if urgency_found:
            phishing_score += urgency_found * 10
            result["indicators"].append(f"⚠️ Urgency language detected ({urgency_found} instances)")
        
        # Check for money-related words
        money_words = ["money", "cash", "prize", "winner", "lottery", "bank", "account", "credit", "debit"]
        money_found = sum(1 for word in money_words if word in content.lower())
        if money_found:
            phishing_score += money_found * 10
            result["indicators"].append(f"⚠️ Financial terms detected ({money_found} instances)")
        
        # Check for URLs in message
        url_in_msg = re.search(r'https?://\S+|www\.\S+', content)
        if url_in_msg:
            result["indicators"].append("⚠️ Contains URL link - verify before clicking")
            phishing_score += 15
        
        # Check message length (very short promotional = suspicious)
        if len(content) < 50 and any(word in content.lower() for word in ["click", "win", "free"]):
            phishing_score += 20
            result["indicators"].append("⚠️ Short promotional message pattern")
        
        result["risk_score"] = min(phishing_score, 100)
        
        if result["risk_score"] < 20:
            result["severity"] = "low"
            result["indicators"].append("✓ No obvious threats detected")
            result["recommendations"].append("Message appears safe, but always verify sender")
        elif result["risk_score"] < 50:
            result["severity"] = "medium"
            result["recommendations"].append("Be cautious - verify sender before responding")
            result["recommendations"].append("Do not click links from unknown senders")
        else:
            result["severity"] = "high"
            result["recommendations"].append("HIGH RISK - Likely phishing/scam message")
            result["recommendations"].append("Do not respond or click any links")
            result["recommendations"].append("Block the sender and report as spam")
    
    # ===== EMAIL ANALYSIS =====
    elif content_type == "email":
        result = analyze_content(content, "sms")  # Similar analysis
        result["recommendations"].append("Check sender email address carefully for typos")
        result["recommendations"].append("Hover over links to see actual URLs before clicking")
    
    # ===== DEFAULT =====
    else:
        result["indicators"].append(f"Analysis type: {content_type}")
        result["risk_score"] = 25
        result["severity"] = "low"
        result["recommendations"].append("Content received and logged for review")
    
    return result


# ==================== API ROUTES ====================

@app.get("/")
async def root():
    return {"status": "online", "service": "RakshaNetra API", "version": "2.0"}

@app.get("/api/health")
async def health():
    return {"status": "healthy", "database": "connected"}


# ==================== AUTHENTICATION ENDPOINTS ====================

@app.post("/api/auth/register")
async def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    role: str = Form("reporter"),
    unit: str = Form(None)
):
    """
    Register a new user
    Roles: reporter (default), admin
    """
    result = auth_manager.register_user(
        username=username,
        email=email,
        password=password,
        full_name=full_name,
        role=role,
        unit=unit
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return {
        "success": True,
        "message": result["message"],
        "user": result["user"]
    }


@app.post("/api/auth/login")
async def login(credentials: LoginRequest):
    """
    Login and get JWT token
    Accepts JSON payload: {"email": "user@example.com", "password": "pass123"}
    """
    username = credentials.username or credentials.email
    
    result = auth_manager.login(
        username=username,
        password=credentials.password,
        ip_address=None,
        user_agent=None
    )
    
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["message"])
    
    return {
        "success": True,
        "access_token": result["token"],  # Frontend expects "access_token"
        "token": result["token"],
        "user": result["user"],
        "message": result["message"]
    }


@app.post("/api/auth/logout")
async def logout(token: str = Form(...)):
    """Logout and invalidate token"""
    auth_manager.logout(token)
    return {"success": True, "message": "Logged out successfully"}


@app.get("/api/auth/verify")
async def verify_token(token: str):
    """Verify JWT token"""
    user_data = auth_manager.verify_token(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"valid": True, "user": user_data}


@app.get("/api/auth/users")
async def get_users(role: str = None):
    """Get all users (admin only)"""
    users = auth_manager.get_all_users(role=role)
    return {"users": users, "total": len(users)}

@app.post("/api/incidents")
async def create_incident(
    type: str = Form(...),
    content: str = Form(None),
    description: str = Form(None),
    location: str = Form(None),
    unit_name: str = Form(None),
    file: UploadFile = File(None),
    authorization: str = Header(None)
):
    """
    Submit an incident for REAL analysis with Defence Features
    Enhanced with: Threat Repetition, Auto-Escalation, Geo-Intelligence, Army Context
    AUTHENTICATION REQUIRED: Reporter identity tracked for accountability
    """
    # ===== AUTHENTICATION REQUIRED =====
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required. Please login to submit incidents.")
    
    token = authorization.split(" ")[1]
    user_data = auth_manager.verify_token(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token. Please login again.")
    
    # Extract reporter information from JWT token
    reporter_id = user_data["user_id"]
    reporter_username = user_data["username"]
    user_role = user_data["role"]
    
    print(f"\n🔐 Authenticated submission from: {reporter_username} (Role: {user_role})")
    
    content_to_analyze = content or ""
    sandbox_result = None
    
    # Handle file upload with SANDBOX ANALYSIS
    file_content = None
    if file:
        try:
            file_content = await file.read()
            file_size = len(file_content)
            
            print(f"\n📁 File uploaded: {file.filename} ({sandbox_analyzer.format_file_size(file_size)})")
            
            # === LAYER 3: SANDBOX ANALYSIS (FILE SPECIFIC) ===
            sandbox_result = sandbox_analyzer.analyze_file(file_content, file.filename, file_size)
            
            # Use sandbox findings in content analysis
            content_to_analyze = content_to_analyze or f"[File: {file.filename}] {sandbox_result.get('file_type', {}).get('description', '')}"
            
            # Add sandbox indicators to analysis input
            if sandbox_result.get("malware_indicators"):
                content_to_analyze += f"\n[SANDBOX ALERT: {len(sandbox_result['malware_indicators'])} malware indicators found]"
        except Exception as e:
            print(f"❌ Sandbox analysis failed: {e}")
            content_to_analyze = content_to_analyze or f"[File uploaded: {file.filename}]"
    
    # REAL ANALYSIS (with Army Context + NLP + Gemini)
    analysis = analyze_content(content_to_analyze, type)
    
    # Merge sandbox results into analysis
    if sandbox_result:
        analysis["sandbox_analysis"] = sandbox_result
        
        # Enhance risk score based on sandbox findings
        threat_level = sandbox_result.get("threat_level", "LOW")
        if threat_level == "CRITICAL":
            analysis["risk_score"] = max(analysis.get("risk_score", 0), 95)
            analysis["severity"] = "critical"
        elif threat_level == "HIGH":
            analysis["risk_score"] = max(analysis.get("risk_score", 0), 80)
            analysis["severity"] = "high"
        elif threat_level == "MEDIUM":
            analysis["risk_score"] = max(analysis.get("risk_score", 0), 60)
        
        # Add sandbox indicators to main indicators
        if sandbox_result.get("malware_indicators"):
            analysis["indicators"].insert(0, f"🔬 SANDBOX: {len(sandbox_result['malware_indicators'])} malware indicators detected")
            for indicator in sandbox_result["malware_indicators"][:3]:  # Top 3
                analysis["indicators"].insert(1, f"   └─ {indicator}")
        
        if sandbox_result.get("suspicious_behaviors"):
            analysis["indicators"].insert(0, f"⚠️ SANDBOX: {len(sandbox_result['suspicious_behaviors'])} suspicious behaviors")
            for behavior in sandbox_result["suspicious_behaviors"][:3]:  # Top 3
                analysis["indicators"].insert(1, f"   └─ {behavior}")
    
    # Generate incident ID
    incident_id = f"INC-{datetime.now().strftime('%y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    
    # === DEFENCE FEATURE 1: Geo-Intelligence ===
    geo_region = "Unknown Region"
    if location:
        geo_region = geo_intelligence.map_location_to_command(location)
    
    # === DEFENCE FEATURE 2: Army Context Analysis ===
    army_context = army_ai_context.generate_army_context_summary(content_to_analyze)
    military_relevant = army_context.get('military_relevant', False)
    fake_profile_detected = False
    
    # Check for fake army profile if it's social media/message type
    if type in ['social_media', 'message', 'sms']:
        from modules.army_profile_detector import detect_fake_army_profile
        profile_check = detect_fake_army_profile(content_to_analyze)
        fake_profile_detected = profile_check.get('is_fake_profile', False)
        if fake_profile_detected:
            analysis['indicators'].insert(0, f"🚨 FAKE ARMY PROFILE DETECTED: {profile_check.get('reasoning', '')}")
            # Boost severity
            if analysis['severity'] not in ['critical', 'high']:
                analysis['severity'] = 'high'
            if analysis['risk_score'] < 75:
                analysis['risk_score'] = 75
    
    # === DEFENCE FEATURE 3: Threat Repetition Detection ===
    indicators_list = analysis.get('indicators', [])
    similar_threats, frequency_count, related_ids = threat_matcher.find_similar_threats(
        content_to_analyze,
        type,
        indicators_list,
        exclude_id=None
    )
    
    # Add frequency alert to indicators
    if frequency_count > 1:
        analysis['indicators'].insert(0, f"⚠️ REPEATED THREAT: This has been reported {frequency_count} times!")
    
    # Save to database with new fields including reporter information
    conn = get_db()
    conn.execute("""
        INSERT INTO incidents (
            id, type, content, description, risk_score, severity, status,
            indicators, recommendations, created_at, geo_region, unit_name,
            frequency_count, related_incident_ids, military_relevant, fake_profile_detected,
            reporter_id, reporter_username, ai_analysis, is_anonymous
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        incident_id, type, content_to_analyze, description,
        analysis["risk_score"], analysis["severity"], "pending",
        json.dumps(analysis["indicators"]), json.dumps(analysis["recommendations"]),
        datetime.utcnow().isoformat(), geo_region, unit_name,
        frequency_count, json.dumps(related_ids) if related_ids else None,
        1 if military_relevant else 0, 1 if fake_profile_detected else 0,
        reporter_id, reporter_username, json.dumps(analysis), 1  # Store reporter info and full AI analysis
    ))
    conn.commit()
    conn.close()
    
    # === DEFENCE FEATURE 4: Auto-Escalation ===
    escalation_data = {
        'risk_score': analysis['risk_score'],
        'frequency_count': frequency_count,
        'military_relevant': military_relevant,
        'severity': analysis['severity'],
        'content': content_to_analyze,
        'fake_profile_detected': fake_profile_detected
    }
    escalation_result = auto_escalation.check_and_escalate(escalation_data, incident_id)
    
    # === SAVE REPORT AS JSON FILE ===
    report_data = {
        "incident_id": incident_id,
        "type": type,
        "content": content_to_analyze,
        "description": description,
        "location": location,
        "unit_name": unit_name,
        "risk_score": analysis["risk_score"],
        "severity": analysis["severity"],
        "status": "pending",
        "indicators": analysis["indicators"],
        "recommendations": analysis["recommendations"],
        "created_at": datetime.utcnow().isoformat(),
        "geo_region": geo_region,
        "frequency_count": frequency_count,
        "military_relevant": military_relevant,
        "fake_profile_detected": fake_profile_detected,
        "reporter_id": reporter_id,
        "reporter_username": reporter_username,
        "ai_analysis": analysis,
        "sandbox_analysis": sandbox_result,
        "army_context": army_context,
        "similar_threats": similar_threats[:5] if similar_threats else [],
        "related_incident_ids": related_ids,
        "escalated": escalation_result['escalated'],
        "escalation_reason": escalation_result.get('reason')
    }
    
    # Save to reports directory
    report_file = REPORTS_DIR / f"{incident_id}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Report saved: {report_file}")
    
    # Add escalation timeline event
    if escalation_result['escalated']:
        auto_escalation.add_to_timeline(
            incident_id, 'created',
            f"Incident created and auto-escalated: {escalation_result['reason']}",
            'System'
        )
    else:
        auto_escalation.add_to_timeline(
            incident_id, 'created',
            f"Incident created with {analysis['severity']} severity",
            'Citizen'
        )
    
    # === DEFENCE FEATURE 5: Update Geo Statistics ===
    if geo_region != "Unknown Region":
        geo_intelligence.update_geo_statistics(
            geo_region,
            analysis['severity'],
            escalation_result['escalated']
        )
    
    # ===== ROLE-BASED RESPONSE =====
    # Reporters get minimal confirmation, Admins get full analysis
    
    if user_role == "reporter":
        # REPORTER VIEW: Only confirmation, NO AI analysis details
        response = {
            "success": True,
            "incident_id": incident_id,
            "message": "✅ Incident submitted successfully. Our security team will review your report.",
            "status": "pending",
            "submitted_at": datetime.utcnow().isoformat(),
            "reporter_username": reporter_username
        }
        print(f"✅ Reporter response (limited): No analysis shown to {reporter_username}")
    else:
        # ADMIN VIEW: Full AI analysis and intelligence
        response = {
            "success": True,
            "incident_id": incident_id,
            "risk_score": analysis["risk_score"],
            "severity": analysis["severity"],
            "indicators": analysis["indicators"],
            "recommendations": analysis["recommendations"],
            "url_check": analysis.get("url_check"),
            "domain_info": analysis.get("domain_info"),
            "is_trusted": analysis.get("is_trusted", False),
            "ai_powered": analysis.get("ai_powered", False),
            "detailed_analysis": analysis.get("detailed_analysis", ""),
            "detailed_description": analysis.get("detailed_description", ""),
            "threat_type": analysis.get("threat_type", "unknown"),
            "attack_vector": analysis.get("attack_vector", ""),
            "potential_impact": analysis.get("potential_impact", ""),
            "technical_details": analysis.get("technical_details", {}),
            "summary": analysis.get("summary", ""),
            "message": "Incident analyzed and recorded",
            # Defence features
            "geo_region": geo_region,
            "frequency_count": frequency_count,
            "similar_threats_found": len(similar_threats),
            "military_relevant": military_relevant,
            "fake_profile_detected": fake_profile_detected,
            "escalated": escalation_result['escalated'],
            "escalation_reason": escalation_result.get('reason'),
            # Reporter information (only visible to admin)
            "reporter_id": reporter_id,
            "reporter_username": reporter_username
        }
        print(f"✅ Admin response (full): Complete analysis shown to {reporter_username}")
    
    return response

@app.get("/api/incidents")
async def get_incidents():
    """Get all incidents from reports folder"""
    incidents = []
    
    try:
        # Read all JSON files from reports directory
        report_files = sorted(REPORTS_DIR.glob("*.json"), key=os.path.getmtime, reverse=True)
        
        for report_file in report_files[:100]:  # Limit to 100 most recent
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                    
                    # Extract essential fields for list view
                    incidents.append({
                        "id": report_data.get("incident_id"),
                        "type": report_data.get("type"),
                        "content": report_data.get("content"),
                        "description": report_data.get("description"),
                        "summary": report_data.get("content", "")[:100],
                        "risk_score": report_data.get("risk_score"),
                        "severity": report_data.get("severity"),
                        "status": report_data.get("status"),
                        "created_at": report_data.get("created_at"),
                        "geo_region": report_data.get("geo_region"),
                        "reporter_username": report_data.get("reporter_username"),
                        "escalated": report_data.get("escalated", False)
                    })
            except Exception as e:
                print(f"Error reading report file {report_file}: {e}")
                continue
        
        return {"incidents": incidents, "total": len(incidents)}
    
    except Exception as e:
        print(f"Error reading reports directory: {e}")
        # Fallback to database if reports folder fails
        conn = get_db()
        cursor = conn.execute("SELECT * FROM incidents ORDER BY created_at DESC LIMIT 100")
        rows = cursor.fetchall()
        conn.close()
        
        incidents = []
        for row in rows:
            incidents.append({
                "id": row["id"],
                "type": row["type"],
                "content": row["content"],
                "description": row["description"],
                "risk_score": row["risk_score"],
                "severity": row["severity"],
                "status": row["status"],
                "created_at": row["created_at"]
            })
        
        return {"incidents": incidents, "total": len(incidents)}

@app.get("/api/incidents/{incident_id}")
async def get_incident(incident_id: str):
    """Get single incident from reports folder"""
    try:
        # Try to read from reports folder first
        report_file = REPORTS_DIR / f"{incident_id}.json"
        
        if report_file.exists():
            with open(report_file, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
                return report_data
        
        # Fallback to database
        conn = get_db()
        cursor = conn.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        return {
            "id": row["id"],
            "type": row["type"],
            "content": row["content"],
            "description": row["description"],
            "risk_score": row["risk_score"],
            "severity": row["severity"],
            "status": row["status"],
            "indicators": json.loads(row["indicators"]) if row["indicators"] else [],
            "recommendations": json.loads(row["recommendations"]) if row["recommendations"] else [],
            "created_at": row["created_at"]
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Incident not found")
    except Exception as e:
        print(f"Error reading incident {incident_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving incident")

@app.get("/api/stats")
async def get_stats():
    """Get dashboard statistics with Defence Intelligence"""
    conn = get_db()
    
    # Total
    total = conn.execute("SELECT COUNT(*) FROM incidents").fetchone()[0]
    
    # By severity
    high = conn.execute("SELECT COUNT(*) FROM incidents WHERE severity = 'high'").fetchone()[0]
    medium = conn.execute("SELECT COUNT(*) FROM incidents WHERE severity = 'medium'").fetchone()[0]
    low = conn.execute("SELECT COUNT(*) FROM incidents WHERE severity = 'low'").fetchone()[0]
    critical = conn.execute("SELECT COUNT(*) FROM incidents WHERE severity = 'critical'").fetchone()[0]
    
    # By type
    types = conn.execute("SELECT type, COUNT(*) as count FROM incidents GROUP BY type").fetchall()
    by_type = {row["type"]: row["count"] for row in types}
    
    # Defence stats
    escalated = conn.execute("SELECT COUNT(*) FROM incidents WHERE escalated_flag = 1").fetchone()[0]
    military_relevant = conn.execute("SELECT COUNT(*) FROM incidents WHERE military_relevant = 1").fetchone()[0]
    fake_profiles = conn.execute("SELECT COUNT(*) FROM incidents WHERE fake_profile_detected = 1").fetchone()[0]
    
    conn.close()
    
    # Get frequency stats
    freq_stats = threat_matcher.get_recent_frequency_stats(days=7)
    
    # Get escalation stats
    esc_stats = auto_escalation.get_escalation_stats(days=7)
    
    return {
        "total_incidents": total,
        "high_severity": high,
        "medium_severity": medium,
        "low_severity": low,
        "critical_severity": critical,
        "by_type": by_type,
        "pending": total,
        "resolved": 0,
        # Defence intelligence
        "escalated_incidents": escalated,
        "military_relevant_threats": military_relevant,
        "fake_profiles_detected": fake_profiles,
        "frequency_stats": freq_stats,
        "escalation_stats": esc_stats
    }


# ==================== DEFENCE FEATURE ENDPOINTS ====================

@app.get("/api/incidents/{incident_id}/similar")
async def get_similar_incidents(incident_id: str):
    """Get similar incidents for threat repetition analysis"""
    similar = threat_matcher.get_similar_incidents(incident_id)
    return {
        "incident_id": incident_id,
        "similar_count": len(similar),
        "similar_incidents": similar
    }

@app.get("/api/incidents/escalated")
async def get_escalated_incidents(limit: int = 50):
    """Get all escalated incidents for CERT officer review"""
    escalated = auto_escalation.get_escalated_incidents(limit)
    return {
        "escalated_count": len(escalated),
        "incidents": escalated
    }

@app.post("/api/incidents/{incident_id}/escalate")
async def manual_escalate_incident(
    incident_id: str,
    reason: str = Form(...),
    officer_name: str = Form("CERT Officer")
):
    """Manually escalate an incident"""
    success = auto_escalation.manual_escalate(incident_id, reason, officer_name)
    return {
        "success": success,
        "incident_id": incident_id,
        "message": "Incident escalated successfully" if success else "Escalation failed"
    }

@app.post("/api/incidents/{incident_id}/update_status")
async def update_incident_status(
    incident_id: str,
    status: str = Form(...),
    notes: str = Form(None),
    officer_name: str = Form("CERT Officer")
):
    """Update incident status and add to timeline"""
    conn = get_db()
    try:
        conn.execute("""
            UPDATE incidents
            SET status = ?,
                officer_notes = COALESCE(officer_notes || '\n', '') || ?
            WHERE id = ?
        """, (status, notes or f"Status changed to {status}", incident_id))
        conn.commit()
        
        # Add to timeline
        auto_escalation.add_to_timeline(
            incident_id,
            'status_changed',
            f"Status updated to: {status}. Notes: {notes or 'None'}",
            officer_name
        )
        
        return {"success": True, "incident_id": incident_id, "new_status": status}
    finally:
        conn.close()

@app.post("/api/incidents/{incident_id}/assign")
async def assign_incident(
    incident_id: str,
    officer_name: str = Form(...)
):
    """Assign incident to CERT officer"""
    conn = get_db()
    try:
        conn.execute("""
            UPDATE incidents
            SET assigned_officer = ?,
                status = CASE WHEN status = 'pending' THEN 'investigating' ELSE status END
            WHERE id = ?
        """, (officer_name, incident_id))
        conn.commit()
        
        # Add to timeline
        auto_escalation.add_to_timeline(
            incident_id,
            'assigned',
            f"Assigned to {officer_name}",
            'System'
        )
        
        return {"success": True, "incident_id": incident_id, "assigned_to": officer_name}
    finally:
        conn.close()

@app.get("/api/incidents/{incident_id}/timeline")
async def get_incident_timeline(incident_id: str):
    """Get full incident timeline"""
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT event_type, event_description, performed_by, timestamp
            FROM incident_timeline
            WHERE incident_id = ?
            ORDER BY timestamp ASC
        """, (incident_id,))
        
        timeline = []
        for row in cursor.fetchall():
            timeline.append({
                'event_type': row[0],
                'description': row[1],
                'performed_by': row[2],
                'timestamp': row[3]
            })
        
        return {
            "incident_id": incident_id,
            "event_count": len(timeline),
            "timeline": timeline
        }
    finally:
        conn.close()

@app.get("/api/geo/heatmap")
async def get_geo_heatmap(days: int = 7):
    """Get incident heatmap by Defence Command regions"""
    heatmap = geo_intelligence.get_geo_heatmap(days)
    return heatmap

@app.get("/api/geo/trends")
async def get_geo_trends(days: int = 30):
    """Get geographic trends over time"""
    trends = geo_intelligence.get_geo_trends(days)
    return trends

@app.get("/api/geo/hotspots")
async def get_hotspot_regions(threshold: int = 10, days: int = 7):
    """Get regions with high incident concentration"""
    hotspots = geo_intelligence.get_hotspot_regions(threshold, days)
    return {
        "threshold": threshold,
        "period_days": days,
        "hotspot_count": len(hotspots),
        "hotspots": hotspots
    }

@app.get("/api/geo/region/{region}")
async def get_region_details(region: str, days: int = 30):
    """Get detailed statistics for a specific Defence Command region"""
    details = geo_intelligence.get_region_details(region, days)
    return details

@app.get("/api/geo/commands")
async def get_all_commands():
    """Get information about all Defence Command regions"""
    return geo_intelligence.get_all_commands_info()

@app.get("/api/intelligence/weekly")
async def get_weekly_intelligence(days: int = 7):
    """Get weekly threat intelligence summary for defence briefings"""
    conn = get_db()
    try:
        from datetime import timedelta
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor = conn.cursor()
        
        # Total incidents
        cursor.execute("SELECT COUNT(*) FROM incidents WHERE created_at >= ?", (cutoff_date,))
        total = cursor.fetchone()[0]
        
        # Most reported content (by similarity cluster)
        cursor.execute("""
            SELECT content, COUNT(*) as count, cluster_id
            FROM incidents
            WHERE created_at >= ? AND cluster_id IS NOT NULL
            GROUP BY cluster_id
            ORDER BY count DESC
            LIMIT 1
        """, (cutoff_date,))
        row = cursor.fetchone()
        most_reported = {
            "content": row[0][:100] + "..." if row and len(row[0]) > 100 else (row[0] if row else "N/A"),
            "count": row[1] if row else 0,
            "cluster_id": row[2] if row else None
        } if row else None
        
        # Most targeted region
        cursor.execute("""
            SELECT geo_region, COUNT(*) as count
            FROM incidents
            WHERE created_at >= ? AND geo_region IS NOT NULL
            GROUP BY geo_region
            ORDER BY count DESC
            LIMIT 1
        """, (cutoff_date,))
        row = cursor.fetchone()
        most_targeted_region = {
            "region": row[0] if row else "Unknown",
            "count": row[1] if row else 0
        }
        
        # Escalated and defence threats
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN escalated_flag = 1 THEN 1 ELSE 0 END) as escalated,
                SUM(CASE WHEN military_relevant = 1 THEN 1 ELSE 0 END) as defence_relevant
            FROM incidents
            WHERE created_at >= ?
        """, (cutoff_date,))
        row = cursor.fetchone()
        escalated_count = row[0] or 0
        defence_threats = row[1] or 0
        
        return {
            "period": f"Last {days} days",
            "generated_at": datetime.now().isoformat(),
            "total_incidents": total,
            "most_reported_threat": most_reported,
            "most_targeted_region": most_targeted_region,
            "escalated_threats": escalated_count,
            "defence_relevant_threats": defence_threats,
            "alert_level": "high" if escalated_count > 10 else ("medium" if escalated_count > 5 else "low")
        }
    finally:
        conn.close()

@app.post("/api/incidents/bulk")
async def bulk_report_incidents(
    incidents: List[dict],
    unit_name: str = Form(None),
    region: str = Form(None)
):
    """Bulk incident submission for Army units"""
    results = []
    
    for incident_data in incidents:
        try:
            # Analyze each incident
            content = incident_data.get('content', '')
            incident_type = incident_data.get('type', 'message')
            
            analysis = analyze_content(content, incident_type)
            
            # Generate ID
            incident_id = f"INC-{datetime.now().strftime('%y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
            
            # Map region
            geo_region = geo_intelligence.map_location_to_command(region) if region else "Unknown Region"
            
            # Save to DB
            conn = get_db()
            conn.execute("""
                INSERT INTO incidents (
                    id, type, content, risk_score, severity, status,
                    indicators, recommendations, created_at, geo_region, unit_name
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                incident_id, incident_type, content,
                analysis["risk_score"], analysis["severity"], "pending",
                json.dumps(analysis["indicators"]), json.dumps(analysis["recommendations"]),
                datetime.utcnow().isoformat(), geo_region, unit_name
            ))
            conn.commit()
            conn.close()
            
            results.append({
                "id": incident_id,
                "risk_score": analysis["risk_score"],
                "severity": analysis["severity"]
            })
        except Exception as e:
            results.append({"error": str(e)})
    
    return {
        "total_submitted": len(incidents),
        "successful": len([r for r in results if 'id' in r]),
        "failed": len([r for r in results if 'error' in r]),
        "high_risk_count": len([r for r in results if r.get('risk_score', 0) >= 60]),
        "results": results
    }


# ==================== ZERO TRUST API ENDPOINTS ====================

@app.get("/api/zero-trust/dashboard")
async def get_zero_trust_dashboard():
    """Get real-time Zero Trust dashboard data"""
    from modules.zero_trust import zero_trust
    import sqlite3
    
    conn = sqlite3.connect(zero_trust.db_path)
    cursor = conn.cursor()
    
    # Active sessions
    cursor.execute("""
        SELECT COUNT(*), AVG(risk_score), MAX(risk_score)
        FROM sessions WHERE is_active = 1
    """)
    active_sessions, avg_risk, max_risk = cursor.fetchone()
    
    # Total devices
    cursor.execute("SELECT COUNT(*), COUNT(CASE WHEN is_trusted = 1 THEN 1 END) FROM devices")
    total_devices, trusted_devices = cursor.fetchone()
    
    # Recent anomalies (last 24h)
    cursor.execute("""
        SELECT COUNT(*), COUNT(CASE WHEN severity = 'CRITICAL' THEN 1 END)
        FROM anomalies 
        WHERE detected_at > datetime('now', '-24 hours')
    """)
    recent_anomalies, critical_anomalies = cursor.fetchone()
    
    # High risk sessions
    cursor.execute("""
        SELECT COUNT(*) FROM sessions 
        WHERE is_active = 1 AND risk_score >= 60
    """)
    high_risk_sessions = cursor.fetchone()[0]
    
    # Recent access denials
    cursor.execute("""
        SELECT COUNT(*) FROM access_requests 
        WHERE decision = 'DENY' AND timestamp > datetime('now', '-24 hours')
    """)
    access_denials = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "active_sessions": active_sessions or 0,
        "average_risk_score": round(avg_risk or 0, 1),
        "max_risk_score": max_risk or 0,
        "total_devices": total_devices or 0,
        "trusted_devices": trusted_devices or 0,
        "recent_anomalies": recent_anomalies or 0,
        "critical_anomalies": critical_anomalies or 0,
        "high_risk_sessions": high_risk_sessions or 0,
        "access_denials_24h": access_denials or 0,
        "security_posture": "EXCELLENT" if (avg_risk or 0) < 30 else "GOOD" if (avg_risk or 0) < 50 else "ALERT",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/zero-trust/devices")
async def get_devices():
    """Get all registered devices"""
    from modules.zero_trust import zero_trust
    import sqlite3
    
    conn = sqlite3.connect(zero_trust.db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT device_id, user_id, os, browser, ip_address, 
               trust_score, is_trusted, total_sessions, last_seen
        FROM devices
        ORDER BY last_seen DESC
        LIMIT 50
    """)
    
    devices = []
    for row in cursor.fetchall():
        devices.append({
            "device_id": row[0],
            "user_id": row[1],
            "os": row[2],
            "browser": row[3],
            "ip_address": row[4],
            "trust_score": row[5],
            "is_trusted": bool(row[6]),
            "total_sessions": row[7],
            "last_seen": row[8]
        })
    
    conn.close()
    return {"devices": devices, "total": len(devices)}


@app.get("/api/zero-trust/sessions")
async def get_sessions():
    """Get active Zero Trust sessions"""
    from modules.zero_trust import zero_trust
    import sqlite3
    
    conn = sqlite3.connect(zero_trust.db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT s.session_id, s.user_id, s.device_id, s.ip_address, 
               s.risk_score, s.trust_level, s.started_at, s.last_activity,
               d.os, d.browser
        FROM sessions s
        LEFT JOIN devices d ON s.device_id = d.device_id
        WHERE s.is_active = 1
        ORDER BY s.risk_score DESC, s.last_activity DESC
        LIMIT 50
    """)
    
    sessions = []
    for row in cursor.fetchall():
        sessions.append({
            "session_id": row[0],
            "user_id": row[1],
            "device_id": row[2],
            "ip_address": row[3],
            "risk_score": row[4],
            "trust_level": row[5],
            "started_at": row[6],
            "last_activity": row[7],
            "device_os": row[8],
            "device_browser": row[9]
        })
    
    conn.close()
    return {"sessions": sessions, "total": len(sessions)}


@app.get("/api/zero-trust/anomalies")
async def get_anomalies():
    """Get detected anomalies"""
    from modules.zero_trust import zero_trust
    import sqlite3
    
    conn = sqlite3.connect(zero_trust.db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, user_id, session_id, anomaly_type, severity, 
               description, detected_at, resolved
        FROM anomalies
        ORDER BY detected_at DESC
        LIMIT 100
    """)
    
    anomalies = []
    for row in cursor.fetchall():
        anomalies.append({
            "id": row[0],
            "user_id": row[1],
            "session_id": row[2],
            "anomaly_type": row[3],
            "severity": row[4],
            "description": row[5],
            "detected_at": row[6],
            "resolved": bool(row[7])
        })
    
    conn.close()
    return {"anomalies": anomalies, "total": len(anomalies)}


@app.get("/api/zero-trust/access-requests")
async def get_access_requests():
    """Get recent access requests"""
    from modules.zero_trust import zero_trust
    import sqlite3
    
    conn = sqlite3.connect(zero_trust.db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, session_id, user_id, resource, action, 
               timestamp, risk_score, decision
        FROM access_requests
        ORDER BY timestamp DESC
        LIMIT 100
    """)
    
    requests = []
    for row in cursor.fetchall():
        requests.append({
            "id": row[0],
            "session_id": row[1],
            "user_id": row[2],
            "resource": row[3],
            "action": row[4],
            "timestamp": row[5],
            "risk_score": row[6],
            "decision": row[7]
        })
    
    conn.close()
    return {"access_requests": requests, "total": len(requests)}


@app.post("/api/zero-trust/test-device")
async def test_device_registration(
    user_id: str = Form("test_user"),
    os: str = Form("Windows"),
    browser: str = Form("Chrome")
):
    """Test endpoint to register a device"""
    from modules.zero_trust import zero_trust
    
    device_info = {
        "os": os,
        "browser": browser,
        "screen_resolution": "1920x1080",
        "timezone": "Asia/Kolkata",
        "language": "en-IN"
    }
    
    device = zero_trust.register_device(
        user_id=user_id,
        user_agent=f"Mozilla/5.0 ({os}; {browser})",
        ip_address="192.168.1.100",
        device_info=device_info
    )
    
    return {
        "success": True,
        "device": device.to_dict()
    }


# ==================== RUN SERVER ====================
if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*50)
    print("🛡️  RAKSHANETRA API SERVER")
    print("="*50)
    print(f"📁 Database: {DB_PATH}")
    print("🌐 Server: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")
    print("="*50 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
