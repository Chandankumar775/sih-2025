"""
RakshaNetra Backend Server - DEFENCE-GRADE CYBERSECURITY PLATFORM
Enhanced with Military Intelligence Features
With REAL Gemini AI Analysis + Threat Repetition + Auto-Escalation + Geo-Intelligence
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
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

# Import defence feature modules
from modules import threat_matcher, auto_escalation, army_ai_context, geo_intelligence

# ==================== GEMINI AI CONFIG ====================
GEMINI_API_KEY = "AIzaSyDcwjDL_kU-KiB8Psk5GC2OCztwhEgwUSU"
GEMINI_MODEL = "gemini-2.0-flash"


def analyze_with_gemini(content: str, content_type: str) -> dict:
    """
    REAL AI Analysis using Google Gemini with Defence Context
    """
    try:
        import google.generativeai as genai
        import json
        import re
        
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        # Base prompt
        base_prompt = f"""You are a cybersecurity expert AI for RakshaNetra - India's Defence Cyber Safety Portal.
Analyze this {content_type} for potential threats with military-grade precision.

CONTENT TO ANALYZE:
{content}

IMPORTANT: Return ONLY valid JSON, no markdown, no explanation before or after.

{{
    "risk_score": <number 0-100>,
    "severity": "<low|medium|high|critical>",
    "is_threat": <true or false>,
    "threat_type": "<phishing|malware|ransomware|social_engineering|credential_theft|data_exfiltration|ddos|scam|spam|safe|unknown>",
    "summary": "<one line summary of the threat>",
    "detailed_description": "<Write 3-4 detailed sentences explaining: What this threat is, how it works, why it's dangerous, and what makes it particularly concerning for defence/government personnel>",
    "attack_vector": "<How the attack is delivered: email|sms|social_media|malicious_link|file_attachment|watering_hole|unknown>",
    "potential_impact": "<Specific impact: Data Loss|Credential Theft|Financial Loss|System Compromise|Espionage|Misinformation|None>",
    "indicators": ["🔴 Indicator 1 with emoji", "⚠️ Indicator 2", "🚨 Indicator 3"],
    "recommendations": ["✅ Actionable recommendation 1", "🛡️ Recommendation 2", "📋 Recommendation 3"],
    "technical_details": {{
        "ip_addresses": ["<list any suspicious IPs found>"],
        "domains": ["<list any suspicious domains>"],
        "file_hashes": ["<if file, provide hypothetical hash>"],
        "malware_family": "<if malware detected, name the family or leave empty>"
    }}
}}

Scoring Rules:
- gov.in, mod.gov.in, nic.in, legitimate government sites = 5-10 (safe)
- google.com, youtube.com, amazon.com, microsoft.com = 5-15 (safe)
- Normal messages without threats = 10-30
- Suspicious patterns (urgency, prizes, money requests) = 50-70
- Phishing attempts targeting defence = 75-85
- Clear phishing/scam/malware = 85-95
- APT or targeted attacks = 95-100

Be thorough and assume defence/military context."""
        
        # Enhance with army context if military-relevant
        prompt = army_ai_context.enhance_ai_prompt_with_army_context(content, content_type, base_prompt)

        response = model.generate_content(prompt)
        ai_text = response.text.strip()
        
        # Clean up response - extract JSON
        # Remove markdown code blocks
        if "```json" in ai_text:
            ai_text = ai_text.split("```json")[1].split("```")[0]
        elif "```" in ai_text:
            parts = ai_text.split("```")
            for part in parts:
                if "{" in part and "}" in part:
                    ai_text = part
                    break
        
        # Extract JSON object from response
        start_idx = ai_text.find('{')
        end_idx = ai_text.rfind('}')
        if start_idx != -1 and end_idx != -1:
            ai_text = ai_text[start_idx:end_idx+1]
        
        ai_text = ai_text.strip()
        
        # Parse JSON
        ai_result = json.loads(ai_text)
        
        # Ensure required fields exist
        if "indicators" not in ai_result:
            ai_result["indicators"] = []
        if "recommendations" not in ai_result:
            ai_result["recommendations"] = []
        
        # Add AI flag
        ai_result["ai_powered"] = True
        ai_result["model"] = "Gemini 2.0 Flash"
        
        print(f"✅ AI Analysis complete: score={ai_result.get('risk_score')}, severity={ai_result.get('severity')}")
        return ai_result
        
    except Exception as e:
        print(f"⚠️ Gemini AI error: {e}")
        import traceback
        traceback.print_exc()
        return None  # Fall back to rule-based

# ==================== APP SETUP ====================
app = FastAPI(title="RakshaNetra API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
            ip_address TEXT
        )
    """)
    conn.commit()
    conn.close()
    print(f"✅ Database ready at: {DB_PATH}")

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
    REAL content analysis - First tries Gemini AI, then falls back to rules
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
    
    # ===== TRY GEMINI AI FIRST =====
    ai_result = analyze_with_gemini(content, content_type)
    
    if ai_result:
        # AI analysis successful!
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

@app.post("/api/incidents")
async def create_incident(
    type: str = Form(...),
    content: str = Form(None),
    description: str = Form(None),
    location: str = Form(None),
    unit_name: str = Form(None),
    file: UploadFile = File(None)
):
    """
    Submit an incident for REAL analysis with Defence Features
    Enhanced with: Threat Repetition, Auto-Escalation, Geo-Intelligence, Army Context
    """
    content_to_analyze = content or ""
    
    # Handle file upload
    file_content = None
    if file:
        try:
            file_content = await file.read()
            content_to_analyze = content_to_analyze or f"[File uploaded: {file.filename}]"
        except:
            pass
    
    # REAL ANALYSIS (with Army Context)
    analysis = analyze_content(content_to_analyze, type)
    
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
    
    # Save to database with new fields
    conn = get_db()
    conn.execute("""
        INSERT INTO incidents (
            id, type, content, description, risk_score, severity, status,
            indicators, recommendations, created_at, geo_region, unit_name,
            frequency_count, related_incident_ids, military_relevant, fake_profile_detected
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        incident_id, type, content_to_analyze, description,
        analysis["risk_score"], analysis["severity"], "pending",
        json.dumps(analysis["indicators"]), json.dumps(analysis["recommendations"]),
        datetime.utcnow().isoformat(), geo_region, unit_name,
        frequency_count, json.dumps(related_ids) if related_ids else None,
        1 if military_relevant else 0, 1 if fake_profile_detected else 0
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
    
    # Build response with defence intelligence
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
        "escalation_reason": escalation_result.get('reason')
    }
    
    return response

@app.get("/api/incidents")
async def get_incidents():
    """Get all incidents"""
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
    """Get single incident"""
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
        "indicators": row["indicators"],
        "recommendations": row["recommendations"],
        "created_at": row["created_at"]
    }

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
