"""
AI Threat Analysis Service
Uses Google Gemini or OpenAI for intelligent threat assessment
"""

import re
import json
import socket
import httpx
from urllib.parse import urlparse
from typing import Optional, Dict, Any, List
from app.core.config import settings
from app.models.schemas import AnalysisResult, SeverityLevel, IncidentType

# URL analysis patterns
SUSPICIOUS_URL_PATTERNS = [
    r'(?:login|signin|verify|secure|account|update|confirm)',
    r'(?:\.tk|\.ml|\.ga|\.cf|\.gq)$',  # Free domain TLDs often used in phishing
    r'(?:bit\.ly|tinyurl|goo\.gl|t\.co)',  # URL shorteners
    r'(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',  # IP addresses in URLs
    r'(?:password|passwd|pwd|credential)',
    r'(?:army|defence|defense|military|gov).*(?:\.com|\.net|\.org)',  # Impersonation attempts
]

# Suspicious message patterns
SUSPICIOUS_MESSAGE_PATTERNS = [
    r'(?:urgent|immediately|act now|limited time)',
    r'(?:otp|one.?time|verification|code)',
    r'(?:click here|click below|follow this link)',
    r'(?:account.*suspended|security.*alert|unauthorized.*access)',
    r'(?:winner|lottery|prize|congratulations)',
    r'(?:bank|transfer|payment).*(?:failed|pending|verify)',
]

# Known threat indicators
THREAT_INDICATORS = {
    "phishing": [
        "Domain registered within last 30 days",
        "Mimics official government communication style",
        "Contains urgent action request",
        "Links to external credential capture page",
        "Uses typosquatting techniques",
    ],
    "malware": [
        "File contains executable code",
        "Suspicious macro detected",
        "Known malware signature match",
        "Obfuscated code patterns found",
    ],
    "scam": [
        "Requests sensitive information",
        "Promises unrealistic rewards",
        "Pressure tactics detected",
        "Impersonates authority figure",
    ],
    "spam": [
        "Mass distribution patterns",
        "Unsolicited commercial content",
        "Known spam sender",
    ]
}


class ThreatAnalyzer:
    """AI-powered threat analysis service"""
    
    def __init__(self):
        self.gemini_available = bool(settings.GOOGLE_API_KEY)
        self.openai_available = bool(settings.OPENAI_API_KEY)
        
        if self.gemini_available:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GOOGLE_API_KEY)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
            except Exception:
                self.gemini_available = False
    
    async def analyze_incident(
        self, 
        incident_type: IncidentType,
        content: str,
        description: Optional[str] = None,
        file_info: Optional[Dict[str, Any]] = None
    ) -> AnalysisResult:
        """
        Analyze an incident and return threat assessment
        """
        
        # Try AI analysis first
        if self.gemini_available:
            try:
                return await self._analyze_with_gemini(incident_type, content, description)
            except Exception as e:
                print(f"Gemini analysis failed: {e}")
        
        # Fallback to rule-based analysis
        return self._rule_based_analysis(incident_type, content, description)
    
    async def _analyze_with_gemini(
        self,
        incident_type: IncidentType,
        content: str,
        description: Optional[str] = None
    ) -> AnalysisResult:
        """Use Google Gemini for AI-powered analysis"""
        
        prompt = f"""You are a cyber security analyst for the Indian Defence Forces. 
Analyze the following {incident_type.value} for potential security threats.

Content to analyze:
{content}

{f"Additional context: {description}" if description else ""}

Respond ONLY with a valid JSON object in this exact format:
{{
    "risk_score": <number 0-100>,
    "severity": "<one of: critical, high, medium, low>",
    "summary": "<brief 2-3 sentence summary of the threat>",
    "indicators": ["<list of specific threat indicators found>"],
    "recommendations": ["<list of actionable security recommendations>"]
}}

Consider:
- Phishing attempts targeting defence personnel
- Social engineering tactics
- Malware distribution methods
- Impersonation of government/military entities
- Data exfiltration attempts

Be thorough but concise. Focus on defence-relevant threats."""

        try:
            response = self.gemini_model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', result_text)
            if json_match:
                result_data = json.loads(json_match.group())
                
                return AnalysisResult(
                    risk_score=min(100, max(0, int(result_data.get("risk_score", 50)))),
                    severity=SeverityLevel(result_data.get("severity", "medium").lower()),
                    summary=result_data.get("summary", "Analysis complete."),
                    indicators=result_data.get("indicators", [])[:10],
                    recommendations=result_data.get("recommendations", [])[:10],
                    iocs=[]
                )
        except Exception as e:
            print(f"Gemini parsing error: {e}")
        
        # Fallback
        return self._rule_based_analysis(incident_type, content, description)
    
    def _rule_based_analysis(
        self,
        incident_type: IncidentType,
        content: str,
        description: Optional[str] = None
    ) -> AnalysisResult:
        """Rule-based fallback analysis"""
        
        content_lower = content.lower() if content else ""
        description_lower = description.lower() if description else ""
        combined = f"{content_lower} {description_lower}"
        
        risk_score = 0
        indicators = []
        threat_type = "unknown"
        
        if incident_type == IncidentType.URL:
            risk_score, indicators = self._analyze_url(content)
            threat_type = "phishing"
        elif incident_type == IncidentType.MESSAGE:
            risk_score, indicators = self._analyze_message(content)
            threat_type = "scam" if risk_score > 50 else "spam"
        else:
            risk_score = 60  # Files get baseline high risk
            indicators = ["File requires manual analysis", "Potential malware vector"]
            threat_type = "malware"
        
        # Determine severity
        if risk_score >= 80:
            severity = SeverityLevel.CRITICAL
        elif risk_score >= 60:
            severity = SeverityLevel.HIGH
        elif risk_score >= 40:
            severity = SeverityLevel.MEDIUM
        else:
            severity = SeverityLevel.LOW
        
        # Generate summary
        summary = self._generate_summary(incident_type, threat_type, risk_score)
        
        # Get recommendations
        recommendations = self._get_recommendations(threat_type, severity)
        
        return AnalysisResult(
            risk_score=risk_score,
            severity=severity,
            summary=summary,
            indicators=indicators,
            recommendations=recommendations,
            iocs=[]
        )
    
    def _analyze_url(self, url: str) -> tuple[int, List[str]]:
        """Analyze URL for threats"""
        indicators = []
        url_lower = url.lower().strip()
        
        # List of trusted/safe domains - these get very low risk scores
        TRUSTED_DOMAINS = [
            'youtube.com', 'youtu.be', 'google.com', 'google.co.in',
            'facebook.com', 'fb.com', 'instagram.com', 'twitter.com', 'x.com',
            'linkedin.com', 'whatsapp.com', 'telegram.org',
            'microsoft.com', 'apple.com', 'amazon.com', 'amazon.in',
            'flipkart.com', 'myntra.com', 'paytm.com',
            'github.com', 'stackoverflow.com', 'reddit.com',
            'wikipedia.org', 'wikimedia.org',
            'gov.in', 'nic.in', 'army.mil', 'indianarmy.nic.in',
            'sbi.co.in', 'hdfcbank.com', 'icicibank.com',
            'irctc.co.in', 'indianrailways.gov.in',
            'gmail.com', 'outlook.com', 'yahoo.com',
            'netflix.com', 'hotstar.com', 'primevideo.com',
            'zoom.us', 'meet.google.com', 'teams.microsoft.com',
        ]
        
        # First, validate if this is actually a URL
        url_pattern = r'^(https?://|www\.)[a-zA-Z0-9][-a-zA-Z0-9@:%._\+~#=]{0,255}\.[a-z]{2,10}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)$'
        ip_url_pattern = r'^https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        
        is_valid_url = bool(re.match(url_pattern, url_lower, re.IGNORECASE)) or bool(re.match(ip_url_pattern, url_lower))
        
        # Also check for simple domain patterns without protocol
        simple_domain = r'^[a-zA-Z0-9][-a-zA-Z0-9]*\.[a-z]{2,10}(/.*)?$'
        if not is_valid_url:
            is_valid_url = bool(re.match(simple_domain, url_lower))
        
        if not is_valid_url:
            # Not a valid URL - return very low risk
            return 5, ["This does not appear to be a valid URL", "Please enter a complete URL starting with http:// or https://"]
        
        # Check if URL is from a trusted domain FIRST
        for trusted in TRUSTED_DOMAINS:
            if trusted in url_lower:
                return 5, [f"This is a well-known trusted website ({trusted})", "No threat detected - safe to access"]
        
        # Valid URL but not trusted - now analyze for threats
        risk_score = 20
        
        for pattern in SUSPICIOUS_URL_PATTERNS:
            if re.search(pattern, url_lower):
                risk_score += 15
                
        # Check for common red flags
        if any(x in url_lower for x in ['login', 'signin', 'verify', 'secure']):
            indicators.append("Contains login/verification keywords")
            risk_score += 10
            
        if any(x in url_lower for x in ['army', 'defence', 'military', 'gov', 'sena']):
            if not any(trusted in url_lower for trusted in ['.gov.in', '.nic.in', '.mil']):
                indicators.append("Mimics official government/military domain")
                risk_score += 25
                
        if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url_lower):
            indicators.append("Uses IP address instead of domain name")
            risk_score += 20
            
        if any(x in url_lower for x in ['.tk', '.ml', '.ga', '.cf', '.xyz']):
            indicators.append("Uses free/suspicious domain TLD common in phishing")
            risk_score += 15
            
        if len(url) > 100:
            indicators.append("Unusually long URL - possible obfuscation")
            risk_score += 10
            
        if '@' in url:
            indicators.append("Contains @ symbol - URL obfuscation technique")
            risk_score += 15
            
        # Check for legitimate government domains - reduce risk
        if any(url_lower.endswith(x) for x in ['.gov.in', '.nic.in', '.mil', 'army.mil']):
            indicators.append("Legitimate government/military domain")
            risk_score = max(10, risk_score - 30)
        
        if not indicators:
            indicators.append("URL structure appears normal - no obvious threat indicators")
            
        return min(100, risk_score), indicators
    
    def _analyze_message(self, message: str) -> tuple[int, List[str]]:
        """Analyze message content for threats"""
        risk_score = 15
        indicators = []
        msg_lower = message.lower()
        
        for pattern in SUSPICIOUS_MESSAGE_PATTERNS:
            if re.search(pattern, msg_lower):
                risk_score += 12
                
        # Check for urgency indicators
        if any(x in msg_lower for x in ['urgent', 'immediately', 'within 24 hours', 'act now']):
            indicators.append("Contains urgent action request")
            risk_score += 15
            
        # Check for credential requests
        if any(x in msg_lower for x in ['otp', 'password', 'pin', 'cvv', 'account number']):
            indicators.append("Requests sensitive credentials")
            risk_score += 20
            
        # Check for impersonation
        if any(x in msg_lower for x in ['army hq', 'defence ministry', 'bank manager', 'collector']):
            indicators.append("Impersonates authority figure")
            risk_score += 20
            
        # Check for reward/prize scams
        if any(x in msg_lower for x in ['winner', 'lottery', 'prize', 'lakhs', 'crores']):
            indicators.append("Contains prize/lottery claim")
            risk_score += 15
            
        # Check for links
        if 'http' in msg_lower or 'www.' in msg_lower:
            indicators.append("Contains external link")
            risk_score += 10
            
        if not indicators:
            indicators.append("Message appears relatively safe")
            
        return min(100, risk_score), indicators
    
    def _generate_summary(self, incident_type: IncidentType, threat_type: str, risk_score: int) -> str:
        """Generate threat summary"""
        
        severity_word = "critical" if risk_score >= 80 else "high" if risk_score >= 60 else "moderate" if risk_score >= 40 else "low"
        
        summaries = {
            IncidentType.URL: f"This URL has been analyzed by Sentinel AI. The link exhibits {severity_word} risk characteristics commonly associated with {threat_type} attempts targeting defence personnel. Exercise caution before interacting with this resource.",
            IncidentType.MESSAGE: f"This message has been analyzed by Sentinel AI. The content shows {severity_word} risk indicators suggesting potential {threat_type} activity. The communication patterns indicate possible social engineering targeting defence personnel or their families.",
            IncidentType.FILE: f"This file has been flagged for {severity_word} risk. The file type and characteristics suggest potential {threat_type} delivery mechanism. Manual inspection by CERT analysts is recommended before opening.",
        }
        
        return summaries.get(incident_type, "Content analyzed. Review recommendations below.")
    
    def _get_recommendations(self, threat_type: str, severity: SeverityLevel) -> List[str]:
        """Get actionable recommendations based on threat type"""
        
        base_recommendations = [
            "Report this incident to your unit IT security officer",
            "Do not interact with the suspicious content",
        ]
        
        threat_recommendations = {
            "phishing": [
                "Block the URL at firewall level",
                "Check if any credentials were entered on this site",
                "Change passwords for any accounts that may have been compromised",
                "Scan affected devices for malware",
            ],
            "malware": [
                "Do not open or execute the file",
                "Quarantine the file for analysis",
                "Run full antivirus scan on the system",
                "Check for unusual system activity",
            ],
            "scam": [
                "Do not respond to the message",
                "Block the sender",
                "Do not share any personal or financial information",
                "Warn colleagues about similar scam attempts",
            ],
            "spam": [
                "Mark as spam and delete",
                "Add sender to block list",
            ]
        }
        
        recommendations = base_recommendations + threat_recommendations.get(threat_type, [])
        
        if severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]:
            recommendations.insert(0, "IMMEDIATE ACTION REQUIRED - Escalate to CERT-Army")
            
        return recommendations[:7]  # Limit to 7 recommendations


# Singleton instance
threat_analyzer = ThreatAnalyzer()


async def analyze_threat(
    incident_type: IncidentType,
    content: str,
    description: Optional[str] = None,
    file_info: Optional[Dict[str, Any]] = None
) -> AnalysisResult:
    """Main function to analyze threats"""
    return await threat_analyzer.analyze_incident(
        incident_type=incident_type,
        content=content,
        description=description,
        file_info=file_info
    )
