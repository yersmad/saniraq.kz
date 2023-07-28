from fastapi import FastAPI, Response, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from .ads_repository import Ad, AdsRepository, AdCreate
from .users_repository import User, UsersRepository, UserCreate
from .database import Base, engine, SessionLocal


Base.metadata.create_all(bind=engine)

app = FastAPI()

ads_repository = AdsRepository()
users_repository = UsersRepository()


class UserCreateRequest(BaseModel):
    username: str
    phone: str
    password: str
    name: str
    city: str

class UserProfileResponse(BaseModel):
    id: int
    username: str
    phone: str
    name: str
    city: str


class AdCreateRequest(BaseModel):
    type: str
    price: int
    address: str
    area: float
    rooms_count: int
    description: str


class AdResponse(BaseModel):
    id: int
    type: str
    price: int
    address: str
    area: float
    rooms_count: int
    description: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/auth/users")
def post_signup(input: UserCreateRequest, db: Session = Depends(get_db)):
    created_user = users_repository.create_user(db, UserCreate(
        username=input.username,
        phone=input.phone,
        password=input.password,
        name=input.name,
        city=input.city
    ))

    return Response(status_code=200)
