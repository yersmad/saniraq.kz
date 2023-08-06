from attrs import define
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Double
from sqlalchemy.orm import Session

from .database import Base
from .schemas import UserProfileEdit

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    phone = Column(String, unique=True)
    password = Column(String)
    name = Column(String)
    city = Column(String)


@define
class UserCreate:
    username: str
    phone: str
    password: str
    name: str
    city: str


class UsersRepository:
    def get_user_by_id(self, db: Session, user_id: int) -> User | None:
        return db.query(User).filter(User.id == user_id).first()

    def get_user_by_username(self, db: Session, username: str) -> User | None:
        return db.query(User).filter(User.username == username).first()

    def get_user_by_password(self, db: Session, password: str) -> User | None:
        return db.query(User).filter(User.password == password).first()

    def get_users(self, db: Session, skip: int = 0, limit: int = 100) -> list[User]:
        return db.query(User).offset(skip).limit(limit).all()

    def create_user(self, db: Session, user: UserCreate) -> User:
        db_user = User(
            username=user.username,
            phone=user.phone,
            password=user.password,
            name=user.name,
            city=user.city
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def update_user(self, db: Session, prev_user: User, new_user: UserProfileEdit) -> User:
        db_user = db.query(User).filter(User.id == prev_user.id).update({
            User.phone: new_user.phone,
            User.name: new_user.name,
            User.city: new_user.city
        })
        db.flush()
        db.commit()
