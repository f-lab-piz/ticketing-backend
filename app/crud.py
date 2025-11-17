from typing import Optional

from sqlalchemy.orm import Session
import bcrypt

from . import models, schemas

def get_password_hash(password: str) -> str:
  return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
  return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

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
