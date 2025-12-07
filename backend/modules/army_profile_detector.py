"""
Fake Army Profile Detection Module
Detects fake Army profiles and honeytrap attempts
"""

import re
from typing import Dict, List

# Army ranks from army_ai_context
ARMY_RANKS = [
    'Field Marshal', 'General', 'Lieutenant General', 'Major General',
    'Brigadier', 'Colonel', 'Lieutenant Colonel', 'Major',
    'Captain', 'Lieutenant', 'Second Lieutenant',
    'Subedar Major', 'Subedar', 'Naib Subedar',
    'Havildar', 'Naik', 'Lance Naik', 'Sepoy'
]

# Honeytrap patterns
HONEYTRAP_PATTERNS = [
    'lonely', 'friendship', 'chatting', 'meet you', 'video call',
    'nice profile', 'want to know you', 'looking for friends',
    'posted at', 'on duty', 'border posting',
    'lets chat', 'can we talk', 'whatsapp', 'telegram',
    'feeling lonely', 'need someone', 'talk to me'
]

# Romance/social engineering keywords
ROMANCE_KEYWORDS = [
    'love', 'like you', 'attracted', 'beautiful', 'handsome',
    'marry', 'relationship', 'girlfriend', 'boyfriend',
    'dear', 'darling', 'sweetheart', 'honey'
]

# Suspicious behavior patterns
SUSPICIOUS_BEHAVIORS = {
    'money_request': ['money', 'transfer', 'payment', 'urgent help', 'financial', 'loan', 'bank'],
    'personal_info': ['aadhaar', 'pan card', 'service number', 'posting details', 'unit name', 'password'],
    'urgency': ['urgent', 'immediately', 'right now', 'quickly', 'asap'],
    'military_jargon_wrong': ['posted in', 'duty on', 'regiment no'],  # Wrong usage
}

def detect_army_rank(content: str) -> List[str]:
    """Detect Army ranks mentioned in content"""
    content_lower = content.lower()
    detected = []
    
    for rank in ARMY_RANKS:
        if rank.lower() in content_lower:
            detected.append(rank)
    
    return detected

def detect_honeytrap_patterns(content: str) -> List[str]:
    """Detect honeytrap/social engineering patterns"""
    content_lower = content.lower()
    detected = []
    
    for pattern in HONEYTRAP_PATTERNS:
        if pattern in content_lower:
            detected.append(pattern)
    
    for keyword in ROMANCE_KEYWORDS:
        if keyword in content_lower:
            detected.append(keyword)
    
    return detected

def check_phone_format(content: str) -> Dict:
    """Check if phone numbers are in valid Indian format"""
    # Indian phone: 10 digits starting with 6-9
    phone_pattern = r'\b[6-9]\d{9}\b'
    phones = re.findall(phone_pattern, content)
    
    # Check for invalid formats
    invalid_phones = re.findall(r'\b\d{7,12}\b', content)
    invalid_phones = [p for p in invalid_phones if p not in phones]
    
    return {
        'valid_phones': phones,
        'invalid_phones': invalid_phones,
        'has_valid': len(phones) > 0,
        'has_invalid': len(invalid_phones) > 0
    }

def detect_suspicious_behaviors(content: str) -> Dict[str, List[str]]:
    """Detect various suspicious behaviors"""
    content_lower = content.lower()
    detected = {}
    
    for behavior_type, keywords in SUSPICIOUS_BEHAVIORS.items():
        found = [kw for kw in keywords if kw in content_lower]
        if found:
            detected[behavior_type] = found
    
    return detected

def detect_fake_army_profile(content: str) -> Dict:
    """
    Main function: Detect if content suggests a fake Army profile
    
    Returns confidence score and reasoning
    """
    result = {
        'is_fake_profile': False,
        'confidence': 0,
        'identified_ranks': [],
        'suspicious_behaviors': [],
        'honeytrap_patterns': [],
        'phone_issues': {},
        'reasoning': ''
    }
    
    # 1. Check for Army ranks
    ranks = detect_army_rank(content)
    if ranks:
        result['identified_ranks'] = ranks
        result['confidence'] += 20
    
    # 2. Check for honeytrap/romance patterns
    honeytrap = detect_honeytrap_patterns(content)
    if honeytrap:
        result['honeytrap_patterns'] = honeytrap
        result['confidence'] += len(honeytrap) * 10
        result['suspicious_behaviors'].append(f"Social engineering/honeytrap language detected")
    
    # 3. Check phone number format
    phone_check = check_phone_format(content)
    result['phone_issues'] = phone_check
    
    # If rank mentioned but no valid phone, suspicious
    if ranks and not phone_check['has_valid']:
        result['confidence'] += 15
        result['suspicious_behaviors'].append("Army rank mentioned but no valid phone number")
    
    # If rank mentioned with invalid phone format
    if ranks and phone_check['has_invalid']:
        result['confidence'] += 10
        result['suspicious_behaviors'].append(f"Invalid phone format: {phone_check['invalid_phones']}")
    
    # 4. Check for money/info requests
    suspicious = detect_suspicious_behaviors(content)
    for behavior_type, keywords in suspicious.items():
        if behavior_type == 'money_request':
            result['confidence'] += 30
            result['suspicious_behaviors'].append(f"Financial request detected: {', '.join(keywords[:3])}")
        elif behavior_type == 'personal_info':
            result['confidence'] += 25
            result['suspicious_behaviors'].append(f"Requests sensitive information: {', '.join(keywords[:3])}")
        elif behavior_type == 'urgency':
            result['confidence'] += 10
            result['suspicious_behaviors'].append(f"Urgency tactics: {', '.join(keywords[:3])}")
    
    # 5. Rank + Honeytrap + Money = Very high confidence
    if ranks and honeytrap and 'money_request' in suspicious:
        result['confidence'] += 20
        result['suspicious_behaviors'].append("🚨 TRIPLE RED FLAG: Rank impersonation + Romance/friendship + Money request")
    
    # 6. Check for common scam phrases
    scam_phrases = [
        'army wife', 'officer wife', 'posted abroad', 'peacekeeping mission',
        'coming to India', 'package stuck', 'customs clearance',
        'need help urgently', 'trust you', 'god bless'
    ]
    
    scam_found = [phrase for phrase in scam_phrases if phrase in content.lower()]
    if scam_found:
        result['confidence'] += len(scam_found) * 15
        result['suspicious_behaviors'].append(f"Common scam phrases: {', '.join(scam_found[:3])}")
    
    # Final determination
    result['confidence'] = min(result['confidence'], 100)
    
    if result['confidence'] >= 50:
        result['is_fake_profile'] = True
        
        # Build reasoning
        reason_parts = []
        
        if ranks:
            reason_parts.append(f"Claims to be {ranks[0]}")
        
        if honeytrap:
            reason_parts.append(f"Uses honeytrap tactics ({len(honeytrap)} patterns)")
        
        if 'money_request' in suspicious:
            reason_parts.append("Requests money")
        
        if 'personal_info' in suspicious:
            reason_parts.append("Asks for sensitive info")
        
        if not phone_check['has_valid'] and ranks:
            reason_parts.append("No valid contact details")
        
        result['reasoning'] = f"{result['confidence']}% confidence - " + ", ".join(reason_parts)
    else:
        result['reasoning'] = f"Low confidence ({result['confidence']}%) - Not enough indicators"
    
    return result
