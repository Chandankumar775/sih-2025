"""
Zero Trust Middleware for FastAPI
Automatically evaluates every request with Zero Trust principles
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import time
from datetime import datetime


class ZeroTrustMiddleware:
    """
    Middleware that applies Zero Trust verification to all API requests
    - Device fingerprinting
    - Risk assessment
    - Continuous authorization
    """
    
    def __init__(self, app):
        self.app = app
        
        # Import zero trust module
        try:
            import sys
            import os
            # Add parent directory to path
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if backend_dir not in sys.path:
                sys.path.insert(0, backend_dir)
            
            from modules.zero_trust import zero_trust
            from modules.audit_logger import audit_logger, AuditEventType
            self.zero_trust = zero_trust
            self.audit_logger = audit_logger
            self.enabled = True
            print("[ZERO TRUST] ✅ Middleware enabled")
        except Exception as e:
            print(f"[ZERO TRUST] ❌ Failed to load: {e}")
            self.enabled = False
    
    async def __call__(self, request: Request, call_next):
        """Process each request with Zero Trust evaluation"""
        
        if not self.enabled:
            return await call_next(request)
        
        # Skip Zero Trust for public endpoints
        public_paths = ["/", "/health", "/api/auth/login", "/api/auth/register", "/docs", "/openapi.json"]
        if any(request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)
        
        start_time = time.time()
        
        try:
            # Extract request context
            user_agent = request.headers.get("user-agent", "Unknown")
            ip_address = request.client.host if request.client else "Unknown"
            
            # Extract device info from headers (sent by frontend)
            device_info = {
                "os": request.headers.get("X-Device-OS", "Unknown"),
                "browser": request.headers.get("X-Device-Browser", "Unknown"),
                "screen_resolution": request.headers.get("X-Device-Screen", "Unknown"),
                "timezone": request.headers.get("X-Device-Timezone", "UTC"),
                "language": request.headers.get("accept-language", "en")[:2]
            }
            
            # Get user from request state (set by auth middleware)
            user_id = getattr(request.state, "user_id", None)
            username = getattr(request.state, "username", "anonymous")
            
            if not user_id:
                # Allow public access but still track
                response = await call_next(request)
                return response
            
            # Register/update device
            device = self.zero_trust.register_device(
                user_id=user_id,
                user_agent=user_agent,
                ip_address=ip_address,
                device_info=device_info
            )
            
            # Determine action and resource from request
            action = self._map_http_method_to_action(request.method)
            resource = request.url.path
            
            # Get location context (in production, use IP geolocation API)
            location_context = {
                "location": {
                    "city": "Unknown",
                    "country": "India",  # Default to India for military users
                    "ip": ip_address
                }
            }
            
            # Calculate risk score
            risk_assessment = self.zero_trust.calculate_risk_score(
                user_id=user_id,
                device_id=device.device_id,
                ip_address=ip_address,
                action=action,
                resource=resource,
                context=location_context
            )
            
            # Check if access should be blocked
            if risk_assessment['risk_score'] >= 70:
                # Log blocked access
                self.audit_logger.log_event(
                    event_type=AuditEventType.ACCESS_DENIED,
                    actor=username,
                    action=f"Access denied to {resource}",
                    status="blocked",
                    actor_ip=ip_address,
                    resource_type="api",
                    resource_id=resource,
                    metadata={
                        "risk_score": risk_assessment['risk_score'],
                        "risk_level": risk_assessment['risk_level'],
                        "anomalies": risk_assessment['anomalies_detected']
                    }
                )
                
                # Return 403 Forbidden
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "error": "Access Denied",
                        "message": "Zero Trust security policy violation",
                        "risk_score": risk_assessment['risk_score'],
                        "risk_level": risk_assessment['risk_level'],
                        "recommendation": risk_assessment['recommendation'],
                        "requires_mfa": risk_assessment['requires_mfa'],
                        "requires_approval": risk_assessment['requires_approval']
                    }
                )
            
            # Add Zero Trust context to request
            request.state.zero_trust = {
                "device_id": device.device_id,
                "risk_score": risk_assessment['risk_score'],
                "risk_level": risk_assessment['risk_level'],
                "trust_factors": risk_assessment['trust_factors'],
                "anomalies": risk_assessment['anomalies_detected'],
                "requires_mfa": risk_assessment['requires_mfa']
            }
            
            # Process request
            response = await call_next(request)
            
            # Log successful access
            if response.status_code < 400:
                self.audit_logger.log_event(
                    event_type=AuditEventType.INCIDENT_VIEWED if "GET" in action else AuditEventType.INCIDENT_CREATED,
                    actor=username,
                    action=f"{action} {resource}",
                    status="success",
                    actor_ip=ip_address,
                    resource_type="api",
                    resource_id=resource,
                    metadata={
                        "risk_score": risk_assessment['risk_score'],
                        "device_id": device.device_id
                    }
                )
            
            # Add Zero Trust headers to response
            response.headers["X-Zero-Trust-Score"] = str(risk_assessment['risk_score'])
            response.headers["X-Zero-Trust-Level"] = risk_assessment['risk_level']
            
            processing_time = time.time() - start_time
            response.headers["X-Process-Time"] = f"{processing_time:.4f}"
            
            return response
            
        except Exception as e:
            print(f"[ZERO TRUST] Error processing request: {e}")
            # On error, allow request but log
            return await call_next(request)
    
    def _map_http_method_to_action(self, method: str) -> str:
        """Map HTTP method to action name"""
        mapping = {
            "GET": "view",
            "POST": "create",
            "PUT": "update",
            "PATCH": "update",
            "DELETE": "delete"
        }
        return mapping.get(method.upper(), "access")
