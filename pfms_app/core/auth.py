from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os

security = HTTPBearer()

def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials  
    payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=os.getenv('ALGORITHM'))
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: user ID not found",
        )
    return payload


user:dict=Depends(validate_token)
  
