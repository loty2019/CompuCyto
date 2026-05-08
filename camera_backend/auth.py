"""
Authentication shim for the camera service.

The dashboard now uses local profiles instead of passwords or JWT login.
Endpoints keep their existing Depends(verify_jwt) signatures, but this
function always returns a local operator identity.
"""
from typing import Optional
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer(auto_error=False)


def verify_jwt(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> dict:
    return {"sub": 1, "email": "local@cytocore.local", "role": "operator"}


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[dict]:
    return verify_jwt(credentials)
