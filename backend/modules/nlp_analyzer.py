"""
NLP Analyzer Module for RakshaNetra
Advanced Natural Language Processing for threat detection
Extracts entities, detects urgency, analyzes sentiment
"""

import re
from typing import Dict, List, Any

# Optional imports - spacy has Python 3.14 compatibility issues
try:
    import spacy
    SPACY_AVAILABLE = True
except Exception as e:
    print(f"⚠️  spaCy not available: {e}")
    spacy = None
    SPACY_AVAILABLE = False

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TextBlob = None
    TEXTBLOB_AVAILABLE = False

try:
    from langdetect import detect, LangDetectException
    LANGDETECT_AVAILABLE = True
except ImportError:
    detect = None
    LangDetectException = Exception
    LANGDETECT_AVAILABLE = False

try:
    import phonenumbers
    PHONENUMBERS_AVAILABLE = True
except ImportError:
    phonenumbers = None
    PHONENUMBERS_AVAILABLE = False

# Load spaCy model if available
nlp = None
if SPACY_AVAILABLE:
    try:
        nlp = spacy.load("en_core_web_sm")
    except Exception as e:
        print(f"⚠️  spaCy model not loaded: {e}")
        print("   Run: python -m spacy download en_core_web_sm")
        nlp = None


def analyze_text(content: str, content_type: str) -> Dict[str, Any]:
    """
    Comprehensive NLP analysis of text content
    
    Args:
        content: The text to analyze
        content_type: Type of content (url, text, email, sms)
    
    Returns:
        Dictionary with NLP analysis results
    """
    print(f"\n🔍 NLP Analysis Starting (Fallback Mode: {not SPACY_AVAILABLE})...")
    print(f"Content length: {len(content)} characters")
    
    # If NLP libraries aren't available, return basic analysis
    if not SPACY_AVAILABLE:
        return {
            "entities": extract_entities(content),
            "language": "unknown",
            "sentiment": {"polarity": 0.0, "subjectivity": 0.5, "label": "neutral"},
            "urgency_score": 50,
            "scam_keywords": detect_scam_keywords(content),
            "threat_indicators": detect_threat_patterns(content),
            "analysis_type": "Basic Pattern Matching",
            "confidence": 0.60,
            "note": "Limited analysis - NLP libraries not available"
        }
    
    result = {
        "entities": extract_entities(content),
        "language": detect_language(content),
        "sentiment": analyze_sentiment(content),
        "urgency_score": calculate_urgency(content),
        "scam_keywords": detect_scam_keywords(content),
        "threat_indicators": detect_threat_patterns(content),
        "analysis_type": "NLP",
        "confidence": 0.85
    }
    
    print(f"[OK] NLP Analysis Complete")
    print(f"   - Entities found: {sum(len(v) for v in result['entities'].values())}")
    print(f"   - Urgency: {result['urgency_score']}/100")
    print(f"   - Language: {result['language']}")
    
    return result


def extract_entities(text: str) -> Dict[str, List[str]]:
    """Extract key entities from text using multiple methods"""
    entities = {
        "phone_numbers": [],
        "emails": [],
        "urls": [],
        "bank_names": [],
        "army_ranks": [],
        "money_amounts": [],
        "persons": [],
        "organizations": []
    }
    
    # Extract phone numbers using phonenumbers library
    if PHONENUMBERS_AVAILABLE:
        try:
            for match in phonenumbers.PhoneNumberMatcher(text, "IN"):
                phone = phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164)
                entities["phone_numbers"].append(phone)
        except:
            pass
    
    # Extract phone numbers using regex (backup)
    phone_patterns = [
        r'\+91[-\s]?\d{10}',
        r'\+91\d{10}',
        r'91\d{10}',
        r'\d{10}'
    ]
    for pattern in phone_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            cleaned = re.sub(r'[-\s]', '', match)
            if len(cleaned) >= 10 and cleaned not in str(entities["phone_numbers"]):
                entities["phone_numbers"].append(match)
    
    # Extract emails
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    entities["emails"] = list(set(re.findall(email_pattern, text)))
    
    # Extract URLs
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    entities["urls"] = list(set(re.findall(url_pattern, text)))
    
    # Extract bank names
    bank_keywords = [
        'SBI', 'State Bank of India', 'HDFC', 'ICICI', 'Axis Bank', 'PNB', 
        'Punjab National Bank', 'Bank of Baroda', 'Canara Bank', 'Union Bank',
        'IDBI', 'Yes Bank', 'Kotak', 'IndusInd', 'Federal Bank'
    ]
    for bank in bank_keywords:
        if bank.lower() in text.lower():
            entities["bank_names"].append(bank)
    
    # Extract Indian Army ranks
    army_ranks = [
        'General', 'Lieutenant General', 'Major General', 'Brigadier',
        'Colonel', 'Lieutenant Colonel', 'Major', 'Captain', 'Lieutenant',
        'Subedar', 'Naib Subedar', 'Havildar', 'Sepoy', 'Jawan'
    ]
    for rank in army_ranks:
        if rank.lower() in text.lower():
            entities["army_ranks"].append(rank)
    
    # Extract money amounts
    money_patterns = [
        r'₹\s*\d+(?:,\d+)*(?:\.\d+)?',
        r'Rs\.?\s*\d+(?:,\d+)*(?:\.\d+)?',
        r'\d+(?:,\d+)*\s*(?:rupees|INR)',
    ]
    for pattern in money_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        entities["money_amounts"].extend(matches)
    
    # Use spaCy for person and organization extraction
    if nlp:
        try:
            doc = nlp(text[:1000])  # Limit to first 1000 chars for performance
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    entities["persons"].append(ent.text)
                elif ent.label_ == "ORG":
                    entities["organizations"].append(ent.text)
        except:
            pass
    
    # Remove duplicates and limit results
    for key in entities:
        entities[key] = list(set(entities[key]))[:10]  # Max 10 per category
    
    return entities


def detect_language(text: str) -> str:
    """Detect language of text"""
    if not LANGDETECT_AVAILABLE:
        return "Unknown"
    
    try:
        lang_code = detect(text)
        lang_map = {
            'en': 'English',
            'hi': 'Hindi',
            'ur': 'Urdu',
            'pa': 'Punjabi',
            'bn': 'Bengali',
            'ta': 'Tamil',
            'te': 'Telugu',
            'mr': 'Marathi'
        }
        return lang_map.get(lang_code, lang_code.upper())
    except (LangDetectException, Exception):
        return "Unknown"


def analyze_sentiment(text: str) -> Dict[str, Any]:
    """Analyze sentiment and emotional tone"""
    if not TEXTBLOB_AVAILABLE:
        # Basic pattern-based sentiment
        threat_words = ['attack', 'threat', 'danger', 'kill', 'bomb', 'weapon', 'terror']
        positive_words = ['safe', 'secure', 'protected', 'help']
        
        text_lower = text.lower()
        threat_count = sum(1 for word in threat_words if word in text_lower)
        positive_count = sum(1 for word in positive_words if word in text_lower)
        
        if threat_count > positive_count:
            sentiment = "Negative/Threatening"
            polarity = -0.5
        elif positive_count > threat_count:
            sentiment = "Positive"
            polarity = 0.5
        else:
            sentiment = "Neutral"
            polarity = 0.0
        
        return {
            "sentiment": sentiment,
            "polarity": polarity,
            "subjectivity": 0.5,
            "emotional_tone": "Urgent" if threat_count > 0 else "Calm"
        }
    
    try:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 to 1
        subjectivity = blob.sentiment.subjectivity  # 0 to 1
        
        # Determine sentiment category
        if polarity > 0.1:
            sentiment = "Positive"
        elif polarity < -0.1:
            sentiment = "Negative/Threatening"
        else:
            sentiment = "Neutral"
        
        return {
            "sentiment": sentiment,
            "polarity": round(polarity, 2),
            "subjectivity": round(subjectivity, 2),
            "emotional_tone": "Urgent" if subjectivity > 0.6 else "Calm"
        }
    except:
        return {
            "sentiment": "Unknown",
            "polarity": 0,
            "subjectivity": 0,
            "emotional_tone": "Unknown"
        }


def calculate_urgency(text: str) -> int:
    """Calculate urgency score (0-100) based on urgency indicators"""
    urgency_score = 0
    text_lower = text.lower()
    
    # High urgency words (10 points each)
    high_urgency = [
        'urgent', 'immediately', 'now', 'asap', 'emergency', 'quick',
        'hurry', 'fast', 'expire', 'expires', 'expiring', 'suspended',
        'blocked', 'locked', 'verify now', 'act now', 'limited time',
        'last chance', 'today only', 'within 24 hours'
    ]
    for word in high_urgency:
        if word in text_lower:
            urgency_score += 10
    
    # Medium urgency indicators (5 points each)
    medium_urgency = [
        'please', 'kindly', 'required', 'need', 'must', 'should',
        'confirm', 'update', 'action needed'
    ]
    for word in medium_urgency:
        if word in text_lower:
            urgency_score += 5
    
    # Exclamation marks (5 points each, max 15)
    exclamations = text.count('!')
    urgency_score += min(exclamations * 5, 15)
    
    # ALL CAPS words (15 points if >50% of text)
    caps_words = len([w for w in text.split() if w.isupper() and len(w) > 2])
    if caps_words / max(len(text.split()), 1) > 0.5:
        urgency_score += 15
    
    return min(urgency_score, 100)


def detect_scam_keywords(text: str) -> List[str]:
    """Detect common scam and phishing keywords"""
    keywords_found = []
    text_lower = text.lower()
    
    scam_patterns = {
        "Account Issues": ['account suspended', 'account blocked', 'account locked', 'unusual activity'],
        "Verification": ['verify', 'confirm', 'update details', 'validate', 'authenticate'],
        "Urgency": ['urgent', 'immediately', 'act now', 'expires', 'limited time'],
        "Threats": ['legal action', 'police complaint', 'arrest warrant', 'fine', 'penalty'],
        "Money": ['send money', 'transfer funds', 'payment required', 'refund', 'prize won'],
        "Credentials": ['password', 'pin', 'otp', 'cvv', 'card details', 'account number'],
        "Impersonation": ['bank representative', 'officer', 'manager', 'official', 'government'],
        "Links": ['click here', 'link below', 'visit', 'download', 'install']
    }
    
    for category, keywords in scam_patterns.items():
        for keyword in keywords:
            if keyword in text_lower:
                keywords_found.append(f"{category}: {keyword}")
    
    return keywords_found[:15]  # Limit to top 15


def detect_threat_patterns(text: str) -> Dict[str, Any]:
    """Detect specific threat patterns"""
    patterns = {
        "has_suspicious_url": bool(re.search(r'bit\.ly|tinyurl|goo\.gl|t\.co', text, re.IGNORECASE)),
        "has_ip_address": bool(re.search(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', text)),
        "requests_credentials": bool(re.search(r'password|pin|otp|cvv|card.*number', text, re.IGNORECASE)),
        "mentions_money": bool(re.search(r'₹|\$|rupees|rs\.?|money|payment|transfer', text, re.IGNORECASE)),
        "impersonates_authority": bool(re.search(r'bank|police|government|officer|official|army|military', text, re.IGNORECASE)),
        "creates_urgency": bool(re.search(r'urgent|immediately|now|asap|expire|suspended|blocked', text, re.IGNORECASE)),
        "threatens_consequences": bool(re.search(r'legal action|arrest|fine|penalty|blocked|suspended', text, re.IGNORECASE)),
        "suspicious_sender": bool(re.search(r'unknown|private|hidden|blocked|restricted', text, re.IGNORECASE))
    }
    
    threat_count = sum(patterns.values())
    patterns["threat_level"] = "Critical" if threat_count >= 5 else "High" if threat_count >= 3 else "Medium" if threat_count >= 1 else "Low"
    patterns["total_indicators"] = threat_count
    
    return patterns


def enhance_analysis_with_nlp(content: str, content_type: str) -> Dict[str, Any]:
    """
    Main function to enhance threat analysis with NLP
    This is called from server.py
    """
    try:
        return analyze_text(content, content_type)
    except Exception as e:
        print(f"⚠️  NLP Analysis Error: {e}")
        return {
            "entities": {},
            "language": "Unknown",
            "sentiment": {"sentiment": "Unknown"},
            "urgency_score": 0,
            "scam_keywords": [],
            "threat_indicators": {},
            "error": str(e)
        }


# For testing
if __name__ == "__main__":
    test_text = """
    URGENT! Your SBI account has been suspended due to suspicious activity.
    Please verify your account immediately by calling +91-9876543210 or visit
    http://fake-sbi-verify.tk/login
    Failure to do so will result in permanent account closure within 24 hours.
    """
    
    result = analyze_text(test_text, "sms")
    print("\n" + "="*60)
    print("NLP ANALYSIS RESULTS:")
    print("="*60)
    import json
    print(json.dumps(result, indent=2))
