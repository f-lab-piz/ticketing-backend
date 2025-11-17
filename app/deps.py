import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from .db import get_db
from . import crud, schemas, models

SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-me-in-prod")
ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
  to_encode = data.copy()
  if expires_delta:
    expire = datetime.utcnow() + expires_delta
  else:
    expire = datetime.utcnow() + timedelta(minutes=15)
  to_encode.update({"exp": expire})
  encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
  return encoded_jwt

def decode_access_token(token: str) -> schemas.TokenData:
  credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
  )
  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    subject: Optional[str] = payload.get("sub")
    exp: Optional[int] = payload.get("exp")
    if subject is None:
      raise credentials_exception
    return schemas.TokenData(sub=subject, exp=exp)
  except JWTError:
    raise credentials_exception

  
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
  token_data = decode_access_token(token)

  user = crud.get_user_by_email(db, token_data.sub) if token_data.sub else None
  if user is None:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
  return user
