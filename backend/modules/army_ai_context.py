"""
Army-Aware AI Context Module
Enhances AI analysis with defence-specific threat patterns and context
"""

from typing import List, Dict, Optional, Tuple
import re

# Defence-specific scam patterns
ARMY_SCAM_PATTERNS = {
    'csd_card': {
        'keywords': [
            'CSD card', 'CSD canteen', 'canteen card', 'defence canteen',
            'army canteen', 'CSD renewal', 'canteen membership', 'CSD application',
            'canteen facility', 'CSD quota', 'canteen smart card'
        ],
        'severity_boost': 'high',
        'description': 'CSD (Canteen Stores Department) Card Scam'
    },
    'fake_recruitment': {
        'keywords': [
            'army recruitment', 'defence job', 'soldier vacancy', 'army bharti',
            'BSF recruitment', 'CRPF job', 'military hiring', 'ITBP vacancy',
            'defence job quota', 'ex-serviceman quota', 'army rally',
            'defence selection', 'military job', 'paramilitary recruitment'
        ],
        'severity_boost': 'high',
        'description': 'Fake Army/Defence Recruitment Scam'
    },
    'rank_impersonation': {
        'keywords': [
            'Colonel', 'Major', 'Captain', 'Lieutenant', 'General',
            'Brigadier', 'Subedar', 'Havildar', 'Sepoy', 'Commandant',
            'army officer', 'defence personnel', 'military officer',
            'service number', 'regiment', 'battalion'
        ],
        'severity_boost': 'high',
        'description': 'Army Rank/Officer Impersonation'
    },
    'cantonment_scams': {
        'keywords': [
            'cantonment pass', 'gate pass', 'MES', 'Military Engineering',
            'army quarters', 'defence accommodation', 'station HQ',
            'cantonment board', 'military station', 'defence colony',
            'army housing', 'MES contractor'
        ],
        'severity_boost': 'medium',
        'description': 'Cantonment/Military Station Scam'
    },
    'honeytrap': {
        'keywords': [
            'lonely', 'friendship', 'chatting', 'meet you', 'video call',
            'nice profile', 'army wife', 'defence family', 'officer wife',
            'service person', 'posted at', 'on duty', 'border posting',
            'want to know you', 'looking for friends'
        ],
        'severity_boost': 'critical',
        'description': 'Honeytrap/Social Engineering Attack'
    },
    'pension_scam': {
        'keywords': [
            'defence pension', 'army pension', 'ex-serviceman pension',
            'pension verification', 'ECHS card', 'disability pension',
            'war widow pension', 'gallantry award', 'pension arrears'
        ],
        'severity_boost': 'high',
        'description': 'Defence Pension/ECHS Scam'
    },
    'fake_tender': {
        'keywords': [
            'defence tender', 'army supply', 'military contract',
            'defence procurement', 'MoD tender', 'ordnance factory',
            'defence deal', 'army equipment', 'military supplies'
        ],
        'severity_boost': 'medium',
        'description': 'Fake Defence Tender/Contract Scam'
    }
}

# Indian Army ranks hierarchy
ARMY_RANKS = {
    'commissioned': [
        'Field Marshal', 'General', 'Lieutenant General', 'Major General',
        'Brigadier', 'Colonel', 'Lieutenant Colonel', 'Major',
        'Captain', 'Lieutenant', 'Second Lieutenant'
    ],
    'junior_commissioned': [
        'Subedar Major', 'Subedar', 'Naib Subedar'
    ],
    'other_ranks': [
        'Havildar', 'Naik', 'Lance Naik', 'Sepoy'
    ]
}

# Defence organizations
DEFENCE_ORGS = [
    'Indian Army', 'Indian Navy', 'Indian Air Force',
    'BSF', 'CRPF', 'ITBP', 'CISF', 'SSB', 'NSG', 'Assam Rifles',
    'Ministry of Defence', 'MoD', 'DRDO', 'Ordnance Factory',
    'Defence Research', 'Military Intelligence', 'RAW'
]

def detect_army_scam_type(content: str) -> List[Dict]:
    """Detect which army scam patterns are present"""
    content_lower = content.lower()
    detected_patterns = []
    
    for pattern_name, pattern_data in ARMY_SCAM_PATTERNS.items():
        matches = []
        for keyword in pattern_data['keywords']:
            if keyword.lower() in content_lower:
                matches.append(keyword)
        
        if matches:
            detected_patterns.append({
                'pattern_type': pattern_name,
                'description': pattern_data['description'],
                'severity_boost': pattern_data['severity_boost'],
                'matched_keywords': matches
            })
    
    return detected_patterns

def detect_army_rank(content: str) -> Optional[Dict]:
    """Detect if content mentions Army ranks"""
    content_lower = content.lower()
    
    all_ranks = (
        ARMY_RANKS['commissioned'] +
        ARMY_RANKS['junior_commissioned'] +
        ARMY_RANKS['other_ranks']
    )
    
    detected_ranks = []
    for rank in all_ranks:
        if rank.lower() in content_lower:
            detected_ranks.append(rank)
    
    if detected_ranks:
        # Determine rank category
        highest_rank = detected_ranks[0]
        category = 'other'
        
        if highest_rank in ARMY_RANKS['commissioned']:
            category = 'commissioned_officer'
        elif highest_rank in ARMY_RANKS['junior_commissioned']:
            category = 'junior_commissioned_officer'
        elif highest_rank in ARMY_RANKS['other_ranks']:
            category = 'other_ranks'
        
        return {
            'detected_ranks': detected_ranks,
            'highest_rank': highest_rank,
            'category': category,
            'count': len(detected_ranks)
        }
    
    return None

def detect_defence_org(content: str) -> List[str]:
    """Detect mentions of defence organizations"""
    content_lower = content.lower()
    detected = []
    
    for org in DEFENCE_ORGS:
        if org.lower() in content_lower:
            detected.append(org)
    
    return detected

def is_military_relevant(content: str) -> Tuple[bool, List[str]]:
    """Check if content is relevant to military/defence personnel"""
    reasons = []
    
    # Check for scam patterns
    scam_patterns = detect_army_scam_type(content)
    if scam_patterns:
        reasons.append(f"Detected {len(scam_patterns)} defence-specific scam pattern(s)")
    
    # Check for ranks
    rank_info = detect_army_rank(content)
    if rank_info:
        reasons.append(f"Mentions Army rank: {rank_info['highest_rank']}")
    
    # Check for defence orgs
    orgs = detect_defence_org(content)
    if orgs:
        reasons.append(f"References defence organization(s): {', '.join(orgs[:3])}")
    
    # Additional military keywords
    military_keywords = [
        'soldier', 'serviceman', 'veteran', 'military', 'defence',
        'regiment', 'battalion', 'corps', 'posting', 'deployment'
    ]
    
    content_lower = content.lower()
    found_keywords = [kw for kw in military_keywords if kw in content_lower]
    if found_keywords:
        reasons.append(f"Contains military keywords: {', '.join(found_keywords[:3])}")
    
    is_relevant = len(reasons) > 0
    
    return is_relevant, reasons

def enhance_ai_prompt_with_army_context(content: str, content_type: str, base_prompt: str) -> str:
    """Add defence-specific context to AI analysis prompt"""
    
    # Check military relevance
    is_relevant, relevance_reasons = is_military_relevant(content)
    
    if not is_relevant:
        return base_prompt  # No need to add army context
    
    # Detect specific patterns
    scam_patterns = detect_army_scam_type(content)
    rank_info = detect_army_rank(content)
    orgs = detect_defence_org(content)
    
    # Build army context section
    army_context = f"""
    
🎖️ **DEFENCE/MILITARY CONTEXT DETECTED** 🎖️

This content appears to target Indian Defence personnel. Please analyze with special attention to:

📋 **Common Defence-Targeted Scams:**
1. **CSD Card Scams** - Fake canteen card renewal/application, asking for fees
2. **Fake Army Recruitment** - Fraudulent job offers, fake rally notifications  
3. **Rank Impersonation** - Scammers posing as Army officers (Colonel, Major, etc.)
4. **Cantonment Scams** - Fake gate passes, MES contracts, housing scams
5. **Honeytrap Attacks** - Social engineering targeting servicemen via friendship/romance
6. **Pension Scams** - Fake pension verification, ECHS card fraud
7. **Aadhaar/PAN Linking** - Fake urgent linking messages for defence personnel

"""
    
    if scam_patterns:
        army_context += f"""
⚠️ **DETECTED SCAM PATTERNS in this content:**
"""
        for pattern in scam_patterns:
            army_context += f"- {pattern['description']} (Severity: {pattern['severity_boost']})\n"
            army_context += f"  Matched: {', '.join(pattern['matched_keywords'][:5])}\n"
    
    if rank_info:
        army_context += f"""
🎖️ **RANK MENTION DETECTED:**
- Ranks mentioned: {', '.join(rank_info['detected_ranks'])}
- Category: {rank_info['category']}
- ⚠️ WARNING: Scammers often impersonate high-ranking officers
"""
    
    if orgs:
        army_context += f"""
🏛️ **DEFENCE ORGANIZATION REFERENCES:**
- Organizations: {', '.join(orgs)}
- Verify if sender has legitimate authority to represent these orgs
"""
    
    army_context += """
🔍 **ANALYSIS INSTRUCTIONS FOR DEFENCE CONTENT:**

1. **If Defence-Related Scam Detected:**
   - Set risk_score minimum to 70 (high threat to defence personnel)
   - Upgrade severity to at least "high"
   - Set military_relevant: true
   - Add specific defence recommendations

2. **Red Flags for Defence Personnel:**
   - Money requests from "officers" or "defence officials"
   - Urgent calls to action related to service matters
   - Unofficial communication channels for official matters
   - Romance/friendship approaches mentioning military service
   - Unsolicited job offers or tender opportunities
   - Requests for sensitive information (service number, posting details)

3. **Recommendations Should Include:**
   - Report to Unit Cyber Cell or Station Security Officer
   - Verify through official defence channels only
   - Never share service details with unknown contacts
   - Be cautious of social media friend requests
   - Report to defence.cyber@nic.in if Army-related fraud

**Remember:** Defence personnel are high-value targets. Increase threat assessment accordingly.
"""
    
    # Inject army context into the base prompt
    enhanced_prompt = base_prompt.replace(
        "CONTENT TO ANALYZE:",
        f"{army_context}\n\nCONTENT TO ANALYZE:"
    )
    
    # Add military_relevant field to expected JSON output
    enhanced_prompt = enhanced_prompt.replace(
        '"detailed_analysis":',
        '"military_relevant": <true or false>,\n    "army_scam_type": "<type if detected>",\n    "detailed_analysis":'
    )
    
    return enhanced_prompt

def boost_severity_for_defence_threats(
    ai_result: Dict,
    content: str
) -> Dict:
    """Boost severity and risk score for defence-targeted threats"""
    
    is_relevant, _ = is_military_relevant(content)
    
    if not is_relevant:
        return ai_result
    
    scam_patterns = detect_army_scam_type(content)
    
    # Add military_relevant flag
    ai_result['military_relevant'] = True
    
    if scam_patterns:
        ai_result['army_scam_types'] = [p['description'] for p in scam_patterns]
        
        # Boost severity based on detected patterns
        highest_boost = max([p['severity_boost'] for p in scam_patterns])
        
        severity_mapping = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}
        boost_mapping = {'medium': 1, 'high': 2, 'critical': 3}
        
        current_severity_level = severity_mapping.get(ai_result.get('severity', 'low'), 0)
        boost_level = boost_mapping.get(highest_boost, 0)
        
        new_severity_level = max(current_severity_level, boost_level)
        reverse_mapping = {0: 'low', 1: 'medium', 2: 'high', 3: 'critical'}
        ai_result['severity'] = reverse_mapping[new_severity_level]
        
        # Boost risk score (minimum 70 for defence threats)
        if ai_result.get('risk_score', 0) < 70:
            ai_result['risk_score'] = 70
            ai_result['risk_score_boosted'] = True
            ai_result['boost_reason'] = "Defence-targeted threat"
    
    # Add defence-specific recommendations
    if 'recommendations' not in ai_result:
        ai_result['recommendations'] = []
    
    defence_recommendations = [
        "🎖️ Report to your Unit Cyber Cell or Station Security Officer immediately",
        "🛡️ Verify ANY defence-related communication through official channels only",
        "⚠️ Never share service number, posting details, or unit information",
        "📧 Forward suspicious content to defence.cyber@nic.in"
    ]
    
    # Add defence recommendations if not already present
    for rec in defence_recommendations:
        if not any(rec in existing for existing in ai_result['recommendations']):
            ai_result['recommendations'].insert(0, rec)
    
    return ai_result

def generate_army_context_summary(content: str) -> Dict:
    """Generate complete military context summary for an incident"""
    is_relevant, reasons = is_military_relevant(content)
    
    summary = {
        'military_relevant': is_relevant,
        'relevance_reasons': reasons,
        'scam_patterns': [],
        'rank_mentions': None,
        'defence_orgs': [],
        'threat_assessment': 'none'
    }
    
    if not is_relevant:
        return summary
    
    # Detect patterns
    scam_patterns = detect_army_scam_type(content)
    if scam_patterns:
        summary['scam_patterns'] = [
            {'type': p['description'], 'severity': p['severity_boost']}
            for p in scam_patterns
        ]
    
    rank_info = detect_army_rank(content)
    if rank_info:
        summary['rank_mentions'] = {
            'ranks': rank_info['detected_ranks'],
            'highest': rank_info['highest_rank'],
            'category': rank_info['category']
        }
    
    orgs = detect_defence_org(content)
    if orgs:
        summary['defence_orgs'] = orgs
    
    # Overall threat assessment
    if scam_patterns:
        highest_severity = max([p['severity_boost'] for p in scam_patterns])
        summary['threat_assessment'] = highest_severity
    elif rank_info:
        summary['threat_assessment'] = 'medium'
    else:
        summary['threat_assessment'] = 'low'
    
    return summary
