"""
WatchTower Backend - Main Application
AI-Powered Cyber Incident Portal for Defence
Smart India Hackathon 2025 | Team Urban Dons
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

from app.core.config import settings
from app.routes import auth_router, incidents_router, analytics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print(f"🛡️  {settings.APP_NAME} v{settings.APP_VERSION} starting...")
    print(f"📍 Environment: {settings.APP_ENV}")
    print(f"🔗 CORS Origins: {settings.cors_origins_list}")
    yield
    # Shutdown
    print(f"🛡️  {settings.APP_NAME} shutting down...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    ## WatchTower - AI-Powered Cyber Incident Portal
    
    A comprehensive cyber incident reporting and analysis platform for defence personnel.
    
    ### Features:
    - 🔐 **Secure Authentication** - JWT-based auth with role management
    - 📝 **Incident Reporting** - Submit suspicious URLs, messages, and files
    - 🤖 **AI Analysis** - Automated threat assessment using Google Gemini
    - 📊 **Analytics Dashboard** - Real-time trends and statistics
    - 🚨 **Escalation Workflow** - Route critical threats to CERT-Army
    
    ### Smart India Hackathon 2025
    Problem Statement: SIH25183
    Team: Urban Dons
    """,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }
    )


# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(incidents_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")


# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - Health check"""
    return {
        "status": "operational",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get("/api", tags=["Health"])
async def api_root():
    """API root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.DEBUG else "Disabled in production",
        "endpoints": {
            "auth": "/api/auth",
            "incidents": "/api/incidents",
            "analytics": "/api/analytics"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
