"""
Authentication Routes
Handles login, registration, and token management
"""

from fastapi import APIRouter, HTTPException, status, Depends
from datetime import timedelta
from app.core.config import settings
from app.core.security import (
    create_access_token, 
    get_password_hash, 
    verify_password,
    get_current_user
)
from app.core.database import supabase
from app.models.schemas import (
    LoginRequest, 
    RegisterRequest, 
    TokenResponse, 
    UserResponse,
    MessageResponse
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Demo users for hackathon (matches frontend)
DEMO_USERS = {
    "reporter@army.mil": {
        "id": "demo-user-1",
        "password": "demo123",
        "name": "Field Officer",
        "email": "reporter@army.mil",
        "role": "reporter"
    },
    "admin@rakshanetra.mil": {
        "id": "demo-user-2",
        "password": "demo123",
        "name": "System Admin",
        "email": "admin@rakshanetra.mil",
        "role": "admin"
    }
}


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    """
    Authenticate user and return JWT token
    """
    email = credentials.email.lower()
    
    # Check demo users first (for hackathon demo)
    if email in DEMO_USERS:
        demo_user = DEMO_USERS[email]
        if credentials.password == demo_user["password"]:
            access_token = create_access_token(
                data={
                    "sub": demo_user["id"],
                    "email": demo_user["email"],
                    "role": demo_user["role"],
                    "name": demo_user["name"]
                },
                expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            )
            
            return TokenResponse(
                access_token=access_token,
                token_type="bearer",
                user=UserResponse(
                    id=demo_user["id"],
                    name=demo_user["name"],
                    email=demo_user["email"],
                    role=demo_user["role"]
                )
            )
    
    # Try Supabase auth
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": credentials.password
        })
        
        if auth_response.user:
            user = auth_response.user
            
            # Get user role from user_roles table
            role_result = supabase.table("user_roles").select("role").eq("user_id", user.id).single().execute()
            role = role_result.data.get("role", "reporter") if role_result.data else "reporter"
            
            # Get profile
            profile_result = supabase.table("profiles").select("full_name").eq("user_id", user.id).single().execute()
            name = profile_result.data.get("full_name", "User") if profile_result.data else "User"
            
            access_token = create_access_token(
                data={
                    "sub": str(user.id),
                    "email": user.email,
                    "role": role,
                    "name": name
                }
            )
            
            return TokenResponse(
                access_token=access_token,
                token_type="bearer",
                user=UserResponse(
                    id=str(user.id),
                    name=name,
                    email=user.email,
                    role=role
                )
            )
            
    except Exception as e:
        print(f"Auth error: {e}")
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/register", response_model=TokenResponse)
async def register(data: RegisterRequest):
    """
    Register a new user
    """
    try:
        # Create user in Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": data.email,
            "password": data.password,
            "options": {
                "data": {
                    "full_name": data.name
                }
            }
        })
        
        if auth_response.user:
            user = auth_response.user
            
            # Create profile
            supabase.table("profiles").insert({
                "user_id": str(user.id),
                "full_name": data.name
            }).execute()
            
            # Assign role
            supabase.table("user_roles").insert({
                "user_id": str(user.id),
                "role": data.role.value
            }).execute()
            
            # Generate token
            access_token = create_access_token(
                data={
                    "sub": str(user.id),
                    "email": user.email,
                    "role": data.role.value,
                    "name": data.name
                }
            )
            
            return TokenResponse(
                access_token=access_token,
                token_type="bearer",
                user=UserResponse(
                    id=str(user.id),
                    name=data.name,
                    email=data.email,
                    role=data.role.value
                )
            )
            
    except Exception as e:
        print(f"Registration error: {e}")
        
        # Check if email already exists
        if "already registered" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Registration failed. Please try again."
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout user (client should discard token)
    """
    try:
        supabase.auth.sign_out()
    except:
        pass
    
    return MessageResponse(
        success=True,
        message="Successfully logged out"
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """
    Refresh access token
    """
    access_token = create_access_token(
        data={
            "sub": current_user["id"],
            "email": current_user["email"],
            "role": current_user["role"],
            "name": current_user.get("name", "User")
        }
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=current_user["id"],
            name=current_user.get("name", "User"),
            email=current_user["email"],
            role=current_user["role"]
        )
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current user information
    """
    return UserResponse(
        id=current_user["id"],
        name=current_user.get("name", "User"),
        email=current_user["email"],
        role=current_user["role"]
    )
