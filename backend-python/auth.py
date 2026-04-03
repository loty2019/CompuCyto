"""
JWT Authentication module for FastAPI Camera Service
Validates Bearer tokens using the same secret as NestJS backend
"""
import logging
from typing import Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from config import settings

logger = logging.getLogger(__name__)

# HTTP Bearer token extractor
security = HTTPBearer(auto_error=False)


def verify_jwt(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> dict:
    """
    Validate JWT token from Authorization header.
    Returns decoded payload if valid, raises 401 if invalid/missing.
    
    Token format expected: Bearer <token>
    Payload expected: { sub: userId (number), email: string, ... }
    """
    if not settings.jwt_secret:
        logger.warning("JWT_SECRET not configured - authentication disabled")
        return {"sub": None, "email": None}
    
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        # Decode and verify token using same secret as NestJS
        # Disable strict claim verification since NestJS uses numeric 'sub'
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=["HS256"],
            options={"verify_sub": False}
        )
        
        # Validate required fields
        if "sub" not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        logger.error(f"JWT validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[dict]:
    """
    Optional JWT validation - returns payload if valid token, None if no token.
    Raises 401 only if token is present but invalid.
    Use for endpoints that work with or without auth.
    """
    if credentials is None:
        return None
    
    return verify_jwt(credentials)
