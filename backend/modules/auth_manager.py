"""
Authentication and User Management System
Handles login, signup, JWT tokens, and role-based access control
"""

import sqlite3
import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path
from dataclasses import dataclass


# JWT Configuration
SECRET_KEY = secrets.token_hex(32)  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours


@dataclass
class User:
    """User data structure"""
    user_id: str
    username: str
    email: str
    role: str  # 'reporter', 'analyst', 'admin'
    full_name: str
    unit: Optional[str]
    created_at: str
    is_active: bool
    
    def to_dict(self) -> Dict:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "full_name": self.full_name,
            "unit": self.unit,
            "created_at": self.created_at,
            "is_active": self.is_active
        }


class AuthManager:
    """
    Manages user authentication, registration, and role-based access
    """
    
    def __init__(self, db_path: str = "./auth/users.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize authentication database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT NOT NULL,
                full_name TEXT NOT NULL,
                unit TEXT,
                created_at TEXT NOT NULL,
                last_login TEXT,
                is_active INTEGER DEFAULT 1,
                login_count INTEGER DEFAULT 0
            )
        """)
        
        # Sessions table (for tracking active logins)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                token TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Login attempts (for security)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS login_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                ip_address TEXT,
                success INTEGER NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON user_sessions(user_id)")
        
        conn.commit()
        
        # Create default admin if not exists
        self._create_default_admin(conn, cursor)
        
        conn.close()
    
    def _create_default_admin(self, conn, cursor):
        """Create default admin user for initial setup"""
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        if cursor.fetchone()[0] == 0:
            admin_id = self._generate_user_id()
            salt = secrets.token_hex(16)
            password_hash = self._hash_password("admin123", salt)
            
            cursor.execute("""
                INSERT INTO users (
                    user_id, username, email, password_hash, salt,
                    role, full_name, unit, created_at, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                admin_id, "admin", "admin@rakshanetra.gov.in",
                password_hash, salt, "admin", "System Administrator",
                "Cyber Defence HQ", datetime.utcnow().isoformat(), 1
            ))
            conn.commit()
            print(f"✅ Default admin created - Username: admin, Password: admin123")
    
    def _generate_user_id(self) -> str:
        """Generate unique user ID"""
        return f"USR-{secrets.token_hex(6).upper()}"
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash password with salt using SHA-256"""
        return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
    
    def _create_jwt_token(self, user: User) -> str:
        """Create JWT access token"""
        expires_at = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "exp": expires_at
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    def register_user(
        self,
        username: str,
        email: str,
        password: str,
        full_name: str,
        role: str = "reporter",
        unit: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register a new user
        Returns: {"success": bool, "user": User, "message": str}
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Validate role
        valid_roles = ["reporter", "analyst", "admin"]
        if role not in valid_roles:
            return {"success": False, "message": f"Invalid role. Must be one of: {valid_roles}"}
        
        # Check if username exists
        cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return {"success": False, "message": "Username already exists"}
        
        # Check if email exists
        cursor.execute("SELECT user_id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return {"success": False, "message": "Email already registered"}
        
        # Create user
        user_id = self._generate_user_id()
        salt = secrets.token_hex(16)
        password_hash = self._hash_password(password, salt)
        created_at = datetime.utcnow().isoformat()
        
        cursor.execute("""
            INSERT INTO users (
                user_id, username, email, password_hash, salt,
                role, full_name, unit, created_at, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, username, email, password_hash, salt,
            role, full_name, unit, created_at, 1
        ))
        
        conn.commit()
        conn.close()
        
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            role=role,
            full_name=full_name,
            unit=unit,
            created_at=created_at,
            is_active=True
        )
        
        return {
            "success": True,
            "user": user.to_dict(),
            "message": "User registered successfully"
        }
    
    def login(
        self,
        username: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Authenticate user and return JWT token
        Returns: {"success": bool, "token": str, "user": User, "message": str}
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get user
        cursor.execute("""
            SELECT user_id, username, email, password_hash, salt, role,
                   full_name, unit, created_at, is_active, login_count
            FROM users WHERE username = ?
        """, (username,))
        
        row = cursor.fetchone()
        
        # Log login attempt
        self._log_login_attempt(cursor, username, ip_address, success=row is not None)
        
        if not row:
            conn.commit()
            conn.close()
            return {"success": False, "message": "Invalid username or password"}
        
        user_id, username, email, stored_hash, salt, role, full_name, unit, created_at, is_active, login_count = row
        
        # Check if user is active
        if not is_active:
            conn.close()
            return {"success": False, "message": "Account is deactivated"}
        
        # Verify password
        password_hash = self._hash_password(password, salt)
        if password_hash != stored_hash:
            conn.commit()
            conn.close()
            return {"success": False, "message": "Invalid username or password"}
        
        # Create user object
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            role=role,
            full_name=full_name,
            unit=unit,
            created_at=created_at,
            is_active=True
        )
        
        # Generate JWT token
        token = self._create_jwt_token(user)
        
        # Create session
        session_id = secrets.token_hex(16)
        expires_at = (datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).isoformat()
        
        cursor.execute("""
            INSERT INTO user_sessions (
                session_id, user_id, token, created_at, expires_at,
                ip_address, user_agent, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id, user_id, token, datetime.utcnow().isoformat(),
            expires_at, ip_address, user_agent, 1
        ))
        
        # Update last login
        cursor.execute("""
            UPDATE users SET last_login = ?, login_count = ?
            WHERE user_id = ?
        """, (datetime.utcnow().isoformat(), login_count + 1, user_id))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "token": token,
            "user": user.to_dict(),
            "message": "Login successful"
        }
    
    def _log_login_attempt(self, cursor, username: str, ip_address: Optional[str], success: bool):
        """Log login attempt for security monitoring"""
        cursor.execute("""
            INSERT INTO login_attempts (username, ip_address, success, timestamp)
            VALUES (?, ?, ?, ?)
        """, (username, ip_address, 1 if success else 0, datetime.utcnow().isoformat()))
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify JWT token and return user data
        Returns: {"user_id": str, "username": str, "role": str} or None
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return {
                "user_id": payload["user_id"],
                "username": payload["username"],
                "email": payload["email"],
                "role": payload["role"]
            }
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_id, username, email, role, full_name, unit, created_at, is_active
            FROM users WHERE user_id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return User(
            user_id=row[0],
            username=row[1],
            email=row[2],
            role=row[3],
            full_name=row[4],
            unit=row[5],
            created_at=row[6],
            is_active=bool(row[7])
        )
    
    def get_all_users(self, role: Optional[str] = None) -> list:
        """Get all users, optionally filtered by role"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if role:
            cursor.execute("""
                SELECT user_id, username, email, role, full_name, unit, created_at, is_active, login_count, last_login
                FROM users WHERE role = ?
                ORDER BY created_at DESC
            """, (role,))
        else:
            cursor.execute("""
                SELECT user_id, username, email, role, full_name, unit, created_at, is_active, login_count, last_login
                FROM users
                ORDER BY created_at DESC
            """)
        
        users = []
        for row in cursor.fetchall():
            users.append({
                "user_id": row[0],
                "username": row[1],
                "email": row[2],
                "role": row[3],
                "full_name": row[4],
                "unit": row[5],
                "created_at": row[6],
                "is_active": bool(row[7]),
                "login_count": row[8],
                "last_login": row[9]
            })
        
        conn.close()
        return users
    
    def logout(self, token: str):
        """Invalidate session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE user_sessions SET is_active = 0
            WHERE token = ?
        """, (token,))
        
        conn.commit()
        conn.close()


# Global auth manager instance
auth_manager = AuthManager()
