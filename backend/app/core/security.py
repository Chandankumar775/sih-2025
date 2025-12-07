"""
Security utilities - JWT, password hashing, auth
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer token security
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against hashed password"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Get current user from JWT token"""
    token = credentials.credentials
    payload = decode_token(token)
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    return {
        "id": user_id,
        "email": payload.get("email"),
        "role": payload.get("role", "reporter"),
        "name": payload.get("name")
    }


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[Dict[str, Any]]:
    """Get current user from JWT token (optional - returns None if no token)"""
    if not credentials:
        return {
            "id": "anonymous",
            "email": "anonymous@guest.local",
            "role": "reporter",
            "name": "Anonymous Reporter"
        }
    
    try:
        token = credentials.credentials
        payload = decode_token(token)
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        return {
            "id": user_id,
            "email": payload.get("email"),
            "role": payload.get("role", "reporter"),
            "name": payload.get("name")
        }
    except:
        return {
            "id": "anonymous",
            "email": "anonymous@guest.local",
            "role": "reporter",
            "name": "Anonymous Reporter"
        }


async def require_role(required_roles: list):
    """Dependency to require specific roles"""
    async def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user
    return role_checker


# Pre-made role dependencies
async def get_analyst_or_admin(current_user: dict = Depends(get_current_user)):
    """Require analyst or admin role"""
    if current_user.get("role") not in ["analyst", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Analyst or Admin access required",
        )
    return current_user


async def get_admin_user(current_user: dict = Depends(get_current_user)):
    """Require admin role"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
