"""
Zero Trust Security Framework for RakshaNetra
Implements "Never Trust, Always Verify" principles
- Continuous authentication and authorization
- Device fingerprinting and reputation
- Risk-based access control
- Behavioral analytics
- Session monitoring
"""

import hashlib
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
from pathlib import Path


class RiskLevel(Enum):
    """Risk levels for zero trust scoring"""
    TRUSTED = "TRUSTED"          # Score 0-20
    LOW_RISK = "LOW_RISK"        # Score 21-40
    MEDIUM_RISK = "MEDIUM_RISK"  # Score 41-60
    HIGH_RISK = "HIGH_RISK"      # Score 61-80
    CRITICAL = "CRITICAL"        # Score 81-100


class TrustFactor(Enum):
    """Factors that influence trust score"""
    DEVICE_KNOWN = "DEVICE_KNOWN"
    LOCATION_NORMAL = "LOCATION_NORMAL"
    TIME_NORMAL = "TIME_NORMAL"
    BEHAVIOR_NORMAL = "BEHAVIOR_NORMAL"
    MFA_ENABLED = "MFA_ENABLED"
    VPN_USED = "VPN_USED"
    ARMY_NETWORK = "ARMY_NETWORK"
    RECENT_PASSWORD_CHANGE = "RECENT_PASSWORD_CHANGE"


@dataclass
class DeviceFingerprint:
    """Device identification and reputation"""
    device_id: str
    user_agent: str
    ip_address: str
    os: str
    browser: str
    screen_resolution: str
    timezone: str
    language: str
    first_seen: str
    last_seen: str
    trust_score: int
    is_trusted: bool
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class SessionContext:
    """Context information for zero trust evaluation"""
    session_id: str
    user_id: str
    username: str
    device_id: str
    ip_address: str
    location: Optional[Dict[str, str]]
    timestamp: str
    action: str
    resource: str
    risk_score: int
    trust_factors: List[str]
    anomalies_detected: List[str]
    
    def to_dict(self) -> Dict:
        return asdict(self)


class ZeroTrustFramework:
    """
    Zero Trust Security Implementation
    Continuously evaluates trust and enforces least privilege access
    """
    
    def __init__(self, db_path: str = "./zero_trust/zt.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
        # Indian military network IP ranges (example - should be configured)
        self.trusted_networks = [
            "10.0.0.0/8",      # Private networks
            "172.16.0.0/12",   # Private networks
            "192.168.0.0/16",  # Private networks
        ]
        
        # Trusted locations (Indian defence establishments)
        self.trusted_locations = [
            "New Delhi", "Delhi", "Mumbai", "Bangalore", "Chennai",
            "Pune", "Secunderabad", "Lucknow", "Jabalpur", "Chandigarh"
        ]
    
    def _init_database(self):
        """Initialize Zero Trust database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Device registry
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                device_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                user_agent TEXT NOT NULL,
                ip_address TEXT,
                os TEXT,
                browser TEXT,
                screen_resolution TEXT,
                timezone TEXT,
                language TEXT,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                total_sessions INTEGER DEFAULT 1,
                trust_score INTEGER DEFAULT 50,
                is_trusted INTEGER DEFAULT 0,
                is_blocked INTEGER DEFAULT 0,
                anomaly_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)
        
        # Session tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                device_id TEXT NOT NULL,
                ip_address TEXT NOT NULL,
                location TEXT,
                started_at TEXT NOT NULL,
                last_activity TEXT NOT NULL,
                risk_score INTEGER DEFAULT 0,
                trust_level TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                anomalies TEXT,
                terminated_reason TEXT,
                FOREIGN KEY (device_id) REFERENCES devices(device_id)
            )
        """)
        
        # Access requests (for audit)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS access_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                resource TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                risk_score INTEGER NOT NULL,
                decision TEXT NOT NULL,
                factors TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)
        
        # Behavioral baselines
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS behavior_baseline (
                user_id TEXT PRIMARY KEY,
                typical_hours TEXT,
                typical_locations TEXT,
                typical_devices TEXT,
                average_session_duration INTEGER,
                typical_actions TEXT,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Anomaly detections
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS anomalies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                session_id TEXT,
                anomaly_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT NOT NULL,
                detected_at TEXT NOT NULL,
                resolved INTEGER DEFAULT 0
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_devices_user ON devices(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_access_user ON access_requests(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_anomalies_user ON anomalies(user_id)")
        
        conn.commit()
        conn.close()
    
    def generate_device_id(self, user_agent: str, ip: str, user_id: str) -> str:
        """Generate unique device fingerprint ID"""
        fingerprint = f"{user_agent}|{ip}|{user_id}"
        return hashlib.sha256(fingerprint.encode()).hexdigest()[:16]
    
    def register_device(
        self,
        user_id: str,
        user_agent: str,
        ip_address: str,
        device_info: Dict[str, Any]
    ) -> DeviceFingerprint:
        """Register or update device fingerprint"""
        device_id = self.generate_device_id(user_agent, ip_address, user_id)
        timestamp = datetime.utcnow().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if device exists
        cursor.execute("SELECT * FROM devices WHERE device_id = ?", (device_id,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing device
            cursor.execute("""
                UPDATE devices SET
                    last_seen = ?,
                    total_sessions = total_sessions + 1,
                    ip_address = ?
                WHERE device_id = ?
            """, (timestamp, ip_address, device_id))
            
            # Retrieve updated trust score
            cursor.execute("SELECT trust_score, is_trusted FROM devices WHERE device_id = ?", (device_id,))
            trust_score, is_trusted = cursor.fetchone()
        else:
            # Register new device (starts with medium trust)
            initial_trust = 50
            cursor.execute("""
                INSERT INTO devices (
                    device_id, user_id, user_agent, ip_address, os, browser,
                    screen_resolution, timezone, language, first_seen, last_seen,
                    trust_score, is_trusted, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                device_id, user_id, user_agent, ip_address,
                device_info.get('os', 'Unknown'),
                device_info.get('browser', 'Unknown'),
                device_info.get('screen_resolution', 'Unknown'),
                device_info.get('timezone', 'Unknown'),
                device_info.get('language', 'en'),
                timestamp, timestamp, initial_trust, 0, timestamp
            ))
            trust_score = initial_trust
            is_trusted = 0
        
        conn.commit()
        conn.close()
        
        return DeviceFingerprint(
            device_id=device_id,
            user_agent=user_agent,
            ip_address=ip_address,
            os=device_info.get('os', 'Unknown'),
            browser=device_info.get('browser', 'Unknown'),
            screen_resolution=device_info.get('screen_resolution', 'Unknown'),
            timezone=device_info.get('timezone', 'Unknown'),
            language=device_info.get('language', 'en'),
            first_seen=timestamp if not existing else existing[9],
            last_seen=timestamp,
            trust_score=trust_score,
            is_trusted=bool(is_trusted)
        )
    
    def calculate_risk_score(
        self,
        user_id: str,
        device_id: str,
        ip_address: str,
        action: str,
        resource: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate real-time risk score using multiple factors
        Returns risk assessment with detailed breakdown
        """
        risk_score = 0
        trust_factors = []
        anomalies = []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Factor 1: Device Trust Score (0-30 points)
        cursor.execute("SELECT trust_score, is_trusted, total_sessions FROM devices WHERE device_id = ?", (device_id,))
        device_data = cursor.fetchone()
        
        if device_data:
            device_trust, is_trusted, sessions = device_data
            if device_trust < 30:
                risk_score += 30
                anomalies.append("Untrusted device")
            elif device_trust < 50:
                risk_score += 20
            elif device_trust > 80 and is_trusted:
                trust_factors.append(TrustFactor.DEVICE_KNOWN.value)
                risk_score -= 10  # Bonus for trusted device
            
            if sessions < 3:
                risk_score += 10
                anomalies.append("New device (< 3 sessions)")
        else:
            risk_score += 30
            anomalies.append("Unknown device")
        
        # Factor 2: Location Analysis (0-25 points)
        location = context.get('location', {})
        city = location.get('city', 'Unknown')
        country = location.get('country', 'Unknown')
        
        if country != 'India':
            risk_score += 25
            anomalies.append(f"Access from foreign country: {country}")
        elif city in self.trusted_locations:
            trust_factors.append(TrustFactor.LOCATION_NORMAL.value)
            risk_score -= 5
        else:
            risk_score += 10
        
        # Factor 3: Time of Day Analysis (0-15 points)
        current_hour = datetime.utcnow().hour
        ist_hour = (current_hour + 5) % 24  # Convert to IST
        
        if ist_hour < 6 or ist_hour > 22:
            risk_score += 15
            anomalies.append(f"Unusual access time: {ist_hour}:00 IST")
        else:
            trust_factors.append(TrustFactor.TIME_NORMAL.value)
        
        # Factor 4: Behavioral Analysis (0-20 points)
        cursor.execute("SELECT typical_hours, typical_locations, average_session_duration FROM behavior_baseline WHERE user_id = ?", (user_id,))
        baseline = cursor.fetchone()
        
        if baseline:
            typical_hours = json.loads(baseline[0]) if baseline[0] else []
            typical_locations = json.loads(baseline[1]) if baseline[1] else []
            
            if ist_hour not in typical_hours:
                risk_score += 10
                anomalies.append("Unusual hour compared to user baseline")
            else:
                trust_factors.append(TrustFactor.BEHAVIOR_NORMAL.value)
            
            if city not in typical_locations and len(typical_locations) > 0:
                risk_score += 10
                anomalies.append("Unusual location compared to user baseline")
        
        # Factor 5: Action Sensitivity (0-20 points)
        high_risk_actions = ['export_data', 'delete_incident', 'change_role', 'access_classified']
        medium_risk_actions = ['create_incident', 'update_incident', 'upload_file']
        
        if action in high_risk_actions:
            risk_score += 20
        elif action in medium_risk_actions:
            risk_score += 10
        
        # Factor 6: IP Reputation (0-15 points)
        # Check if IP is from trusted network
        is_trusted_network = self._check_trusted_network(ip_address)
        if is_trusted_network:
            trust_factors.append(TrustFactor.ARMY_NETWORK.value)
            risk_score -= 10
        else:
            risk_score += 10
        
        # Factor 7: Recent Anomalies (0-10 points)
        cursor.execute("""
            SELECT COUNT(*) FROM anomalies 
            WHERE user_id = ? AND detected_at > ? AND resolved = 0
        """, (user_id, (datetime.utcnow() - timedelta(hours=24)).isoformat()))
        recent_anomalies = cursor.fetchone()[0]
        
        if recent_anomalies > 3:
            risk_score += 10
            anomalies.append(f"Multiple recent anomalies: {recent_anomalies}")
        
        conn.close()
        
        # Normalize risk score (0-100)
        risk_score = max(0, min(100, risk_score))
        
        # Determine risk level
        if risk_score <= 20:
            risk_level = RiskLevel.TRUSTED
        elif risk_score <= 40:
            risk_level = RiskLevel.LOW_RISK
        elif risk_score <= 60:
            risk_level = RiskLevel.MEDIUM_RISK
        elif risk_score <= 80:
            risk_level = RiskLevel.HIGH_RISK
        else:
            risk_level = RiskLevel.CRITICAL
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level.value,
            "trust_factors": trust_factors,
            "anomalies_detected": anomalies,
            "requires_mfa": risk_score > 60,
            "requires_approval": risk_score > 80,
            "allow_access": risk_score < 70,
            "recommendation": self._get_recommendation(risk_score, anomalies)
        }
    
    def _check_trusted_network(self, ip: str) -> bool:
        """Check if IP is from trusted military network"""
        # Simplified check - in production, use proper CIDR matching
        return ip.startswith("10.") or ip.startswith("192.168.") or ip.startswith("172.")
    
    def _get_recommendation(self, risk_score: int, anomalies: List[str]) -> str:
        """Get security recommendation based on risk"""
        if risk_score >= 80:
            return "DENY ACCESS - Critical risk detected. Require admin approval and MFA."
        elif risk_score >= 60:
            return "CHALLENGE - High risk detected. Require additional MFA verification."
        elif risk_score >= 40:
            return "MONITOR - Medium risk. Allow but log all actions closely."
        elif risk_score >= 20:
            return "ALLOW - Low risk. Standard monitoring applies."
        else:
            return "ALLOW - Trusted context. Normal operations."
    
    def create_session(
        self,
        user_id: str,
        username: str,
        device_id: str,
        ip_address: str,
        context: Dict[str, Any]
    ) -> SessionContext:
        """Create and track a zero trust session"""
        session_id = hashlib.sha256(f"{user_id}{device_id}{datetime.utcnow()}".encode()).hexdigest()[:24]
        timestamp = datetime.utcnow().isoformat()
        
        # Calculate initial risk
        risk_assessment = self.calculate_risk_score(
            user_id=user_id,
            device_id=device_id,
            ip_address=ip_address,
            action="login",
            resource="session",
            context=context
        )
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Store session
        cursor.execute("""
            INSERT INTO sessions (
                session_id, user_id, device_id, ip_address, location,
                started_at, last_activity, risk_score, trust_level, is_active, anomalies
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id, user_id, device_id, ip_address,
            json.dumps(context.get('location', {})),
            timestamp, timestamp,
            risk_assessment['risk_score'],
            risk_assessment['risk_level'],
            1,
            json.dumps(risk_assessment['anomalies_detected'])
        ))
        
        conn.commit()
        conn.close()
        
        # Log anomalies if any
        if risk_assessment['anomalies_detected']:
            self._log_anomalies(user_id, session_id, risk_assessment['anomalies_detected'])
        
        return SessionContext(
            session_id=session_id,
            user_id=user_id,
            username=username,
            device_id=device_id,
            ip_address=ip_address,
            location=context.get('location'),
            timestamp=timestamp,
            action="login",
            resource="session",
            risk_score=risk_assessment['risk_score'],
            trust_factors=risk_assessment['trust_factors'],
            anomalies_detected=risk_assessment['anomalies_detected']
        )
    
    def verify_access(
        self,
        session_id: str,
        user_id: str,
        action: str,
        resource: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Continuous verification for every access request
        Implements "Never Trust, Always Verify"
        """
        timestamp = datetime.utcnow().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get session info
        cursor.execute("SELECT device_id, ip_address, risk_score FROM sessions WHERE session_id = ? AND is_active = 1", (session_id,))
        session = cursor.fetchone()
        
        if not session:
            return {
                "allowed": False,
                "reason": "Invalid or expired session",
                "risk_score": 100,
                "requires_reauth": True
            }
        
        device_id, ip_address, current_risk = session
        
        # Recalculate risk for this specific action
        risk_assessment = self.calculate_risk_score(
            user_id=user_id,
            device_id=device_id,
            ip_address=ip_address,
            action=action,
            resource=resource,
            context=context
        )
        
        # Make access decision
        decision = "ALLOW" if risk_assessment['allow_access'] else "DENY"
        
        # Log access request
        cursor.execute("""
            INSERT INTO access_requests (
                session_id, user_id, resource, action, timestamp,
                risk_score, decision, factors
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id, user_id, resource, action, timestamp,
            risk_assessment['risk_score'], decision,
            json.dumps({
                "trust_factors": risk_assessment['trust_factors'],
                "anomalies": risk_assessment['anomalies_detected']
            })
        ))
        
        # Update session risk
        cursor.execute("""
            UPDATE sessions SET last_activity = ?, risk_score = ?
            WHERE session_id = ?
        """, (timestamp, risk_assessment['risk_score'], session_id))
        
        conn.commit()
        conn.close()
        
        return {
            "allowed": risk_assessment['allow_access'],
            "risk_score": risk_assessment['risk_score'],
            "risk_level": risk_assessment['risk_level'],
            "requires_mfa": risk_assessment['requires_mfa'],
            "requires_approval": risk_assessment['requires_approval'],
            "recommendation": risk_assessment['recommendation'],
            "trust_factors": risk_assessment['trust_factors'],
            "anomalies": risk_assessment['anomalies_detected']
        }
    
    def _log_anomalies(self, user_id: str, session_id: str, anomalies: List[str]):
        """Log detected anomalies"""
        if not anomalies:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        timestamp = datetime.utcnow().isoformat()
        
        for anomaly in anomalies:
            # Determine severity
            if "foreign country" in anomaly.lower() or "critical" in anomaly.lower():
                severity = "CRITICAL"
            elif "unusual" in anomaly.lower():
                severity = "MEDIUM"
            else:
                severity = "LOW"
            
            cursor.execute("""
                INSERT INTO anomalies (user_id, session_id, anomaly_type, severity, description, detected_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, session_id, "behavioral", severity, anomaly, timestamp))
        
        conn.commit()
        conn.close()
    
    def terminate_session(self, session_id: str, reason: str = "User logout"):
        """Terminate a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE sessions SET is_active = 0, terminated_reason = ?
            WHERE session_id = ?
        """, (reason, session_id))
        
        conn.commit()
        conn.close()
    
    def get_user_risk_profile(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive risk profile for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get devices
        cursor.execute("SELECT COUNT(*), AVG(trust_score) FROM devices WHERE user_id = ?", (user_id,))
        device_count, avg_trust = cursor.fetchone()
        
        # Get recent anomalies
        cursor.execute("""
            SELECT COUNT(*) FROM anomalies 
            WHERE user_id = ? AND detected_at > ? AND resolved = 0
        """, (user_id, (datetime.utcnow() - timedelta(days=7)).isoformat()))
        recent_anomalies = cursor.fetchone()[0]
        
        # Get active sessions
        cursor.execute("SELECT COUNT(*), AVG(risk_score) FROM sessions WHERE user_id = ? AND is_active = 1", (user_id,))
        active_sessions, avg_risk = cursor.fetchone()
        
        conn.close()
        
        overall_risk = int((avg_risk or 50) + (recent_anomalies * 5))
        overall_risk = min(100, overall_risk)
        
        return {
            "user_id": user_id,
            "device_count": device_count or 0,
            "average_device_trust": int(avg_trust or 50),
            "recent_anomalies": recent_anomalies or 0,
            "active_sessions": active_sessions or 0,
            "overall_risk_score": overall_risk,
            "risk_level": RiskLevel.CRITICAL.value if overall_risk > 80 else
                         RiskLevel.HIGH_RISK.value if overall_risk > 60 else
                         RiskLevel.MEDIUM_RISK.value if overall_risk > 40 else
                         RiskLevel.LOW_RISK.value
        }


# Global zero trust instance
zero_trust = ZeroTrustFramework()


# Convenience functions
def register_device(user_id: str, user_agent: str, ip: str, device_info: Dict) -> DeviceFingerprint:
    """Register device with zero trust"""
    return zero_trust.register_device(user_id, user_agent, ip, device_info)


def verify_access_request(session_id: str, user_id: str, action: str, resource: str, context: Dict) -> Dict:
    """Verify access using zero trust"""
    return zero_trust.verify_access(session_id, user_id, action, resource, context)


def calculate_risk(user_id: str, device_id: str, ip: str, action: str, resource: str, context: Dict) -> Dict:
    """Calculate risk score"""
    return zero_trust.calculate_risk_score(user_id, device_id, ip, action, resource, context)
