"""
Authentication shim for Pi-API.

The dashboard now uses passwordless local profiles, so protected endpoint
dependencies resolve to a local operator identity instead of validating JWTs.
"""
from typing import Optional
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer(auto_error=False)


def verify_jwt(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> dict:
    return {"sub": 1, "email": "local@cytocore.local", "role": "operator"}
