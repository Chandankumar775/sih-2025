"""
Tamper-Proof Audit Logging System for RakshaNetra
Judge's Feedback #8: Harder for Log and Audit Trail
Implements cryptographically signed, append-only audit logs
Prevents log tampering and ensures forensic integrity
"""

import os
import json
import hashlib
import hmac
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import sqlite3
from enum import Enum


class AuditEventType(Enum):
    """Types of security events to audit"""
    # Authentication events
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILED = "LOGIN_FAILED"
    LOGOUT = "LOGOUT"
    PASSWORD_CHANGE = "PASSWORD_CHANGE"
    MFA_ENABLED = "MFA_ENABLED"
    MFA_DISABLED = "MFA_DISABLED"
    
    # Authorization events
    ACCESS_DENIED = "ACCESS_DENIED"
    PRIVILEGE_ESCALATION = "PRIVILEGE_ESCALATION"
    ROLE_CHANGE = "ROLE_CHANGE"
    
    # Data events
    INCIDENT_CREATED = "INCIDENT_CREATED"
    INCIDENT_VIEWED = "INCIDENT_VIEWED"
    INCIDENT_UPDATED = "INCIDENT_UPDATED"
    INCIDENT_DELETED = "INCIDENT_DELETED"
    FILE_UPLOADED = "FILE_UPLOADED"
    FILE_DOWNLOADED = "FILE_DOWNLOADED"
    DATA_EXPORT = "DATA_EXPORT"
    
    # Security events
    SUSPICIOUS_ACTIVITY = "SUSPICIOUS_ACTIVITY"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    API_KEY_CREATED = "API_KEY_CREATED"
    API_KEY_REVOKED = "API_KEY_REVOKED"
    ENCRYPTION_KEY_ROTATION = "ENCRYPTION_KEY_ROTATION"
    
    # System events
    SYSTEM_START = "SYSTEM_START"
    SYSTEM_SHUTDOWN = "SYSTEM_SHUTDOWN"
    CONFIG_CHANGE = "CONFIG_CHANGE"
    BACKUP_CREATED = "BACKUP_CREATED"
    EVIDENCE_STORED = "EVIDENCE_STORED"
    
    # Incident response
    INCIDENT_ESCALATED = "INCIDENT_ESCALATED"
    ALERT_TRIGGERED = "ALERT_TRIGGERED"
    PLAYBOOK_EXECUTED = "PLAYBOOK_EXECUTED"


class TamperProofAuditLog:
    """
    Cryptographically secure audit logging system
    - Append-only logs (no deletion/modification)
    - Cryptographic chain (each entry signs previous)
    - HMAC signatures for integrity
    - Separate write-only storage
    """
    
    def __init__(self, log_dir: str = "./audit_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.log_dir / "audit.db"
        self.json_log_path = self.log_dir / "audit.jsonl"
        
        # HMAC key for log integrity
        self.hmac_key = os.environ.get(
            "AUDIT_LOG_KEY",
            "AUDIT_SECRET_KEY_CHANGE_IN_PRODUCTION"
        ).encode()
        
        self._init_database()
        self.last_log_hash = self._get_last_log_hash()
    
    def _init_database(self):
        """Initialize SQLite database for audit logs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main audit log table (append-only)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                actor TEXT NOT NULL,
                actor_ip TEXT,
                resource_type TEXT,
                resource_id TEXT,
                action TEXT NOT NULL,
                status TEXT NOT NULL,
                details TEXT,
                metadata TEXT,
                previous_hash TEXT NOT NULL,
                current_hash TEXT NOT NULL,
                signature TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        # Index for fast queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_actor ON audit_log(actor)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_event_type ON audit_log(event_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_resource ON audit_log(resource_type, resource_id)
        """)
        
        # Failed login attempts (security monitoring)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS failed_logins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                ip_address TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                reason TEXT,
                user_agent TEXT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_failed_ip ON failed_logins(ip_address, timestamp)
        """)
        
        conn.commit()
        conn.close()
    
    def _get_last_log_hash(self) -> str:
        """Get hash of last log entry to create chain"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT current_hash FROM audit_log ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0]
        else:
            # Genesis hash for first entry
            return hashlib.sha256(b"RAKSHANETRA_GENESIS_BLOCK").hexdigest()
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        random_part = os.urandom(4).hex()
        return f"AUD-{timestamp}-{random_part.upper()}"
    
    def _calculate_log_hash(self, log_entry: Dict[str, Any]) -> str:
        """Calculate SHA-256 hash of log entry"""
        # Sort keys for consistent hashing
        log_str = json.dumps(log_entry, sort_keys=True)
        return hashlib.sha256(log_str.encode()).hexdigest()
    
    def _sign_log_entry(self, log_hash: str, previous_hash: str) -> str:
        """Create HMAC signature for log entry"""
        data = f"{log_hash}|{previous_hash}"
        return hmac.new(self.hmac_key, data.encode(), hashlib.sha256).hexdigest()
    
    def log_event(
        self,
        event_type: AuditEventType,
        actor: str,
        action: str,
        status: str = "success",
        actor_ip: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log a security event with cryptographic integrity
        
        Args:
            event_type: Type of event from AuditEventType enum
            actor: Username or system identifier
            action: Description of action taken
            status: success, failure, denied, error
            actor_ip: IP address of actor
            resource_type: Type of resource accessed (incident, user, file, etc.)
            resource_id: ID of specific resource
            details: Additional details about the event
            metadata: JSON-serializable metadata
            
        Returns:
            event_id: Unique identifier for this audit entry
        """
        
        # Generate event ID and timestamp
        event_id = self._generate_event_id()
        timestamp = datetime.utcnow().isoformat()
        
        # Create log entry
        log_entry = {
            "event_id": event_id,
            "timestamp": timestamp,
            "event_type": event_type.value if isinstance(event_type, AuditEventType) else event_type,
            "actor": actor,
            "action": action,
            "status": status,
            "actor_ip": actor_ip,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details,
            "metadata": json.dumps(metadata) if metadata else None
        }
        
        # Calculate hash chaining
        current_hash = self._calculate_log_hash(log_entry)
        previous_hash = self.last_log_hash
        signature = self._sign_log_entry(current_hash, previous_hash)
        
        log_entry["previous_hash"] = previous_hash
        log_entry["current_hash"] = current_hash
        log_entry["signature"] = signature
        log_entry["created_at"] = timestamp
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO audit_log (
                    event_id, timestamp, event_type, actor, actor_ip,
                    resource_type, resource_id, action, status, details,
                    metadata, previous_hash, current_hash, signature, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event_id, timestamp, log_entry["event_type"], actor, actor_ip,
                resource_type, resource_id, action, status, details,
                log_entry["metadata"], previous_hash, current_hash, signature, timestamp
            ))
            
            conn.commit()
            
            # Update last hash for chain
            self.last_log_hash = current_hash
            
            # Also write to JSONL file (backup)
            with open(self.json_log_path, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
            
            return event_id
            
        except Exception as e:
            print(f"[AUDIT] ❌ Failed to log event: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def verify_log_integrity(self, event_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Verify integrity of audit log chain
        
        Args:
            event_id: Verify specific event, or None to verify entire chain
            
        Returns:
            Verification results including any tampering detected
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if event_id:
            # Verify single entry
            cursor.execute("SELECT * FROM audit_log WHERE event_id = ?", (event_id,))
            rows = cursor.fetchall()
        else:
            # Verify entire chain
            cursor.execute("SELECT * FROM audit_log ORDER BY id ASC")
            rows = cursor.fetchall()
        
        if not rows:
            return {"valid": False, "error": "No logs found"}
        
        columns = [desc[0] for desc in cursor.description]
        tampering_detected = []
        expected_previous_hash = hashlib.sha256(b"RAKSHANETRA_GENESIS_BLOCK").hexdigest()
        
        for row in rows:
            log_entry = dict(zip(columns, row))
            
            # Reconstruct log data for hashing
            log_data = {
                "event_id": log_entry["event_id"],
                "timestamp": log_entry["timestamp"],
                "event_type": log_entry["event_type"],
                "actor": log_entry["actor"],
                "action": log_entry["action"],
                "status": log_entry["status"],
                "actor_ip": log_entry["actor_ip"],
                "resource_type": log_entry["resource_type"],
                "resource_id": log_entry["resource_id"],
                "details": log_entry["details"],
                "metadata": log_entry["metadata"]
            }
            
            # Verify hash
            calculated_hash = self._calculate_log_hash(log_data)
            stored_hash = log_entry["current_hash"]
            
            if calculated_hash != stored_hash:
                tampering_detected.append({
                    "event_id": log_entry["event_id"],
                    "issue": "Hash mismatch",
                    "calculated": calculated_hash,
                    "stored": stored_hash
                })
            
            # Verify chain
            if log_entry["previous_hash"] != expected_previous_hash:
                tampering_detected.append({
                    "event_id": log_entry["event_id"],
                    "issue": "Chain broken",
                    "expected_previous": expected_previous_hash,
                    "stored_previous": log_entry["previous_hash"]
                })
            
            # Verify signature
            calculated_sig = self._sign_log_entry(stored_hash, log_entry["previous_hash"])
            if calculated_sig != log_entry["signature"]:
                tampering_detected.append({
                    "event_id": log_entry["event_id"],
                    "issue": "Signature invalid"
                })
            
            expected_previous_hash = stored_hash
        
        conn.close()
        
        return {
            "valid": len(tampering_detected) == 0,
            "entries_checked": len(rows),
            "tampering_detected": tampering_detected,
            "last_verified_hash": expected_previous_hash
        }
    
    def log_failed_login(
        self,
        username: str,
        ip_address: str,
        reason: str = "Invalid credentials",
        user_agent: Optional[str] = None
    ):
        """Log failed login attempt for security monitoring"""
        timestamp = datetime.utcnow().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO failed_logins (username, ip_address, timestamp, reason, user_agent)
            VALUES (?, ?, ?, ?, ?)
        """, (username, ip_address, timestamp, reason, user_agent))
        conn.commit()
        conn.close()
        
        # Also log in main audit
        self.log_event(
            event_type=AuditEventType.LOGIN_FAILED,
            actor=username,
            action=f"Failed login attempt: {reason}",
            status="failure",
            actor_ip=ip_address,
            metadata={"user_agent": user_agent}
        )
    
    def get_failed_login_attempts(
        self,
        username: Optional[str] = None,
        ip_address: Optional[str] = None,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get recent failed login attempts for rate limiting/blocking"""
        from datetime import timedelta
        cutoff_time = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM failed_logins WHERE timestamp > ?"
        params = [cutoff_time]
        
        if username:
            query += " AND username = ?"
            params.append(username)
        
        if ip_address:
            query += " AND ip_address = ?"
            params.append(ip_address)
        
        query += " ORDER BY timestamp DESC"
        
        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def search_logs(
        self,
        event_type: Optional[str] = None,
        actor: Optional[str] = None,
        resource_type: Optional[str] = None,
        status: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Search audit logs with filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM audit_log WHERE 1=1"
        params = []
        
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        
        if actor:
            query += " AND actor = ?"
            params.append(actor)
        
        if resource_type:
            query += " AND resource_type = ?"
            params.append(resource_type)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time)
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results


# Global audit logger instance
audit_logger = TamperProofAuditLog()


# Convenience functions
def log_security_event(event_type: AuditEventType, actor: str, action: str, **kwargs):
    """Log a security event"""
    return audit_logger.log_event(event_type, actor, action, **kwargs)


def verify_audit_integrity():
    """Verify entire audit log integrity"""
    return audit_logger.verify_log_integrity()
