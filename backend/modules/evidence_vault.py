"""
Evidence Vault Module for RakshaNetra
Secure storage and retention of sandbox-analyzed files with chain-of-custody
Implements forensic-grade evidence preservation for military-grade security
"""

import os
import json
import hashlib
import shutil
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
from dataclasses import dataclass, asdict
import hmac


@dataclass
class EvidenceMetadata:
    """Metadata for stored evidence files"""
    evidence_id: str
    original_filename: str
    file_hash_sha256: str
    file_hash_md5: str
    file_size: int
    file_type: str
    threat_level: str
    analysis_timestamp: str
    retention_policy: str  # "30_days", "90_days", "1_year", "permanent"
    incident_id: Optional[str]
    analyst_notes: Optional[str]
    chain_of_custody: List[Dict[str, str]]
    quarantine_status: str  # "active", "archived", "deleted"
    
    def to_dict(self) -> Dict:
        return asdict(self)


class EvidenceVault:
    """
    Military-grade evidence storage system
    - Immutable storage with cryptographic verification
    - Chain-of-custody tracking
    - Retention policies
    - Forensic audit trails
    """
    
    def __init__(self, vault_path: str = "./evidence_vault"):
        self.vault_path = Path(vault_path)
        self.db_path = self.vault_path / "evidence.db"
        self.files_path = self.vault_path / "files"
        self.quarantine_path = self.vault_path / "quarantine"
        self.archive_path = self.vault_path / "archive"
        
        # Create directories
        for path in [self.files_path, self.quarantine_path, self.archive_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        self._init_database()
        
        # Secret key for HMAC (should be in environment variable)
        self.hmac_key = os.environ.get("EVIDENCE_VAULT_KEY", "DEFAULT_SECRET_KEY_CHANGE_ME").encode()
    
    def _init_database(self):
        """Initialize SQLite database for evidence tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evidence (
                evidence_id TEXT PRIMARY KEY,
                original_filename TEXT NOT NULL,
                file_hash_sha256 TEXT NOT NULL UNIQUE,
                file_hash_md5 TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                file_type TEXT NOT NULL,
                threat_level TEXT NOT NULL,
                analysis_timestamp TEXT NOT NULL,
                retention_policy TEXT NOT NULL,
                retention_expires TEXT,
                incident_id TEXT,
                analyst_notes TEXT,
                quarantine_status TEXT NOT NULL,
                storage_path TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                integrity_hash TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chain_of_custody (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                evidence_id TEXT NOT NULL,
                action TEXT NOT NULL,
                actor TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                details TEXT,
                signature TEXT NOT NULL,
                FOREIGN KEY (evidence_id) REFERENCES evidence(evidence_id)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_evidence_hash ON evidence(file_hash_sha256)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_evidence_threat ON evidence(threat_level)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_evidence_status ON evidence(quarantine_status)
        """)
        
        conn.commit()
        conn.close()
    
    def _generate_evidence_id(self, file_hash: str) -> str:
        """Generate unique evidence ID"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"EVD-{timestamp}-{file_hash[:8].upper()}"
    
    def _calculate_integrity_hash(self, metadata: Dict) -> str:
        """Calculate HMAC for evidence integrity verification"""
        # Sort keys for consistent hashing
        sorted_data = json.dumps(metadata, sort_keys=True)
        return hmac.new(self.hmac_key, sorted_data.encode(), hashlib.sha256).hexdigest()
    
    def _sign_action(self, evidence_id: str, action: str, actor: str, timestamp: str) -> str:
        """Create cryptographic signature for chain-of-custody action"""
        data = f"{evidence_id}|{action}|{actor}|{timestamp}"
        return hmac.new(self.hmac_key, data.encode(), hashlib.sha256).hexdigest()
    
    def _calculate_retention_expiry(self, retention_policy: str) -> str:
        """Calculate expiry date based on retention policy"""
        now = datetime.utcnow()
        
        if retention_policy == "30_days":
            expiry = now + timedelta(days=30)
        elif retention_policy == "90_days":
            expiry = now + timedelta(days=90)
        elif retention_policy == "1_year":
            expiry = now + timedelta(days=365)
        elif retention_policy == "permanent":
            return "9999-12-31T23:59:59"
        else:
            expiry = now + timedelta(days=90)  # Default
        
        return expiry.isoformat()
    
    def store_evidence(
        self,
        file_data: bytes,
        original_filename: str,
        file_type: str,
        threat_level: str,
        analysis_results: Dict[str, Any],
        incident_id: Optional[str] = None,
        retention_policy: str = "90_days",
        analyst: str = "system"
    ) -> Dict[str, Any]:
        """
        Store file as evidence with full metadata and chain-of-custody
        
        Args:
            file_data: Raw file bytes
            original_filename: Original filename
            file_type: MIME type or file type
            threat_level: LOW, MEDIUM, HIGH, CRITICAL
            analysis_results: Full sandbox analysis results
            incident_id: Associated incident ID
            retention_policy: Evidence retention policy
            analyst: Who is storing the evidence
            
        Returns:
            Evidence metadata including evidence_id and storage path
        """
        
        # Calculate hashes
        sha256_hash = hashlib.sha256(file_data).hexdigest()
        md5_hash = hashlib.md5(file_data).hexdigest()
        file_size = len(file_data)
        
        # Check if evidence already exists
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT evidence_id FROM evidence WHERE file_hash_sha256 = ?", (sha256_hash,))
        existing = cursor.fetchone()
        
        if existing:
            evidence_id = existing[0]
            print(f"[EVIDENCE] File already exists: {evidence_id}")
            self._add_chain_of_custody(
                evidence_id=evidence_id,
                action="DUPLICATE_SUBMISSION",
                actor=analyst,
                details=f"Duplicate file submitted: {original_filename}"
            )
            conn.close()
            return {"evidence_id": evidence_id, "status": "duplicate"}
        
        # Generate evidence ID
        evidence_id = self._generate_evidence_id(sha256_hash)
        timestamp = datetime.utcnow().isoformat()
        
        # Determine storage location based on threat level
        if threat_level in ["HIGH", "CRITICAL"]:
            storage_dir = self.quarantine_path
            quarantine_status = "active"
        else:
            storage_dir = self.files_path
            quarantine_status = "archived"
        
        # Create evidence subdirectory
        evidence_dir = storage_dir / evidence_id
        evidence_dir.mkdir(parents=True, exist_ok=True)
        
        # Store file
        file_path = evidence_dir / original_filename
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        # Store analysis results
        analysis_path = evidence_dir / "analysis.json"
        with open(analysis_path, 'w') as f:
            json.dump(analysis_results, f, indent=2)
        
        # Calculate retention expiry
        retention_expires = self._calculate_retention_expiry(retention_policy)
        
        # Create metadata
        metadata = {
            "evidence_id": evidence_id,
            "original_filename": original_filename,
            "file_hash_sha256": sha256_hash,
            "file_hash_md5": md5_hash,
            "file_size": file_size,
            "file_type": file_type,
            "threat_level": threat_level,
            "analysis_timestamp": timestamp,
            "retention_policy": retention_policy,
            "retention_expires": retention_expires,
            "incident_id": incident_id,
            "quarantine_status": quarantine_status,
            "storage_path": str(file_path),
            "created_at": timestamp,
            "updated_at": timestamp
        }
        
        # Calculate integrity hash
        integrity_hash = self._calculate_integrity_hash(metadata)
        metadata["integrity_hash"] = integrity_hash
        
        # Store in database
        cursor.execute("""
            INSERT INTO evidence (
                evidence_id, original_filename, file_hash_sha256, file_hash_md5,
                file_size, file_type, threat_level, analysis_timestamp,
                retention_policy, retention_expires, incident_id, analyst_notes,
                quarantine_status, storage_path, created_at, updated_at, integrity_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            evidence_id, original_filename, sha256_hash, md5_hash,
            file_size, file_type, threat_level, timestamp,
            retention_policy, retention_expires, incident_id, None,
            quarantine_status, str(file_path), timestamp, timestamp, integrity_hash
        ))
        
        conn.commit()
        conn.close()
        
        # Add initial chain-of-custody entry
        self._add_chain_of_custody(
            evidence_id=evidence_id,
            action="EVIDENCE_STORED",
            actor=analyst,
            details=f"File stored: {original_filename}, Threat: {threat_level}"
        )
        
        print(f"[EVIDENCE] ✅ Stored: {evidence_id}")
        print(f"[EVIDENCE] Path: {file_path}")
        print(f"[EVIDENCE] SHA256: {sha256_hash}")
        print(f"[EVIDENCE] Status: {quarantine_status}")
        
        return {
            "evidence_id": evidence_id,
            "status": "stored",
            "storage_path": str(file_path),
            "sha256": sha256_hash,
            "threat_level": threat_level,
            "quarantine_status": quarantine_status,
            "retention_expires": retention_expires
        }
    
    def _add_chain_of_custody(
        self,
        evidence_id: str,
        action: str,
        actor: str,
        details: Optional[str] = None
    ):
        """Add chain-of-custody entry with cryptographic signature"""
        timestamp = datetime.utcnow().isoformat()
        signature = self._sign_action(evidence_id, action, actor, timestamp)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chain_of_custody (evidence_id, action, actor, timestamp, details, signature)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (evidence_id, action, actor, timestamp, details, signature))
        conn.commit()
        conn.close()
    
    def verify_evidence_integrity(self, evidence_id: str) -> Dict[str, Any]:
        """Verify evidence integrity using stored hash"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM evidence WHERE evidence_id = ?", (evidence_id,))
        row = cursor.fetchone()
        
        if not row:
            return {"valid": False, "error": "Evidence not found"}
        
        columns = [desc[0] for desc in cursor.description]
        metadata = dict(zip(columns, row))
        stored_integrity = metadata.pop("integrity_hash")
        
        # Recalculate integrity hash
        calculated_integrity = self._calculate_integrity_hash(metadata)
        
        # Verify file hash
        file_path = Path(metadata["storage_path"])
        if file_path.exists():
            with open(file_path, 'rb') as f:
                actual_hash = hashlib.sha256(f.read()).hexdigest()
            file_intact = (actual_hash == metadata["file_hash_sha256"])
        else:
            file_intact = False
        
        conn.close()
        
        return {
            "valid": (stored_integrity == calculated_integrity and file_intact),
            "metadata_integrity": stored_integrity == calculated_integrity,
            "file_integrity": file_intact,
            "evidence_id": evidence_id,
            "file_hash": metadata["file_hash_sha256"]
        }
    
    def get_chain_of_custody(self, evidence_id: str) -> List[Dict[str, Any]]:
        """Retrieve complete chain-of-custody for evidence"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT action, actor, timestamp, details, signature
            FROM chain_of_custody
            WHERE evidence_id = ?
            ORDER BY timestamp ASC
        """, (evidence_id,))
        
        chain = []
        for row in cursor.fetchall():
            chain.append({
                "action": row[0],
                "actor": row[1],
                "timestamp": row[2],
                "details": row[3],
                "signature": row[4]
            })
        
        conn.close()
        return chain
    
    def search_evidence(
        self,
        threat_level: Optional[str] = None,
        status: Optional[str] = None,
        incident_id: Optional[str] = None,
        file_hash: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Search evidence vault with filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM evidence WHERE 1=1"
        params = []
        
        if threat_level:
            query += " AND threat_level = ?"
            params.append(threat_level)
        
        if status:
            query += " AND quarantine_status = ?"
            params.append(status)
        
        if incident_id:
            query += " AND incident_id = ?"
            params.append(incident_id)
        
        if file_hash:
            query += " AND (file_hash_sha256 = ? OR file_hash_md5 = ?)"
            params.extend([file_hash, file_hash])
        
        query += " ORDER BY analysis_timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        columns = [desc[0] for desc in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        conn.close()
        return results
    
    def cleanup_expired_evidence(self) -> Dict[str, int]:
        """Archive expired evidence based on retention policy"""
        now = datetime.utcnow().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT evidence_id, storage_path FROM evidence
            WHERE retention_expires < ? AND quarantine_status = 'active'
        """, (now,))
        
        expired = cursor.fetchall()
        archived_count = 0
        
        for evidence_id, storage_path in expired:
            # Move to archive
            src = Path(storage_path).parent
            dst = self.archive_path / evidence_id
            
            if src.exists():
                shutil.move(str(src), str(dst))
            
            # Update database
            cursor.execute("""
                UPDATE evidence SET quarantine_status = 'archived', updated_at = ?
                WHERE evidence_id = ?
            """, (now, evidence_id))
            
            self._add_chain_of_custody(
                evidence_id=evidence_id,
                action="ARCHIVED_EXPIRED",
                actor="system",
                details="Evidence archived due to retention policy expiry"
            )
            
            archived_count += 1
        
        conn.commit()
        conn.close()
        
        return {
            "archived_count": archived_count,
            "timestamp": now
        }


# Global instance
vault = EvidenceVault()
