from typing import Optional

from pydantic.types import deprecated

from sqlalchemy.orm import Session
from passlib.context import CryptContext

from . import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
  return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
  return pwd_context.verify(plain_password, hashed_password)

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
  return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user_in: schemas.UserCreate) -> models.User:
  hashed = get_password_hash(user_in.password)
  user = models.User(email=user_in.email, hashed_password=hashed)
  db.add(user)
  db.commit()
  db.refresh(user)
  return user

def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
  user = get_user_by_email(db, email)
  if not user:
    return None
  if not verify_password(password, user.hashed_password):
    return None
  return user
