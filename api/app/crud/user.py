# Manejo de las operaciones de base de datos relacionados con usuario

from sqlalchemy.orm import Session
from app.models.users import User
from app.schemas.user import UserCreate

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate, hashed_password: str):
    db_user = User(username=user.username, full_name=user.full_name,role=user.role, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


