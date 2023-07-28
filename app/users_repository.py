from attrs import define
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import Session, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    phone = Column(Integer)
    password = Column(String)
    full_name: Column(String)
    city: Column(String)

    ads = relationship("Ad", back_populates="owner")


@define
class UserCreate:
    username: str
    phone: str
    password: str
    full_name: str
    city: str


class UsersRepository:
    def get_user(self, db: Session, user_id: int) -> User | None:
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
            full_name=user.full_name,
            city=user.city
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
