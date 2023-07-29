from fastapi import FastAPI, Response, Depends, HTTPException, Form
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
    full_name: str
    city: str


class UserProfileResponse(BaseModel):
    id: int
    username: str
    phone: str
    full_name: str
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


def encode_jwt(user_id: int):
    body = {"user_id": user_id}
    token = jwt.encode(body, "test", 'HS256')
    return token


def decode_jwt(token: str):
    data = jwt.decode(token, "test", 'HS256')
    return data["user_id"]


@app.post("/auth/users")
def signup(input: UserCreateRequest, db: Session = Depends(get_db)):
    created_user = users_repository.create_user(db, UserCreate(
        username=input.username,
        phone=input.phone,
        password=input.password,
        full_name=input.full_name,
        city=input.city
    ))

    return Response(status_code=200)


@app.post("/auth/users/login")
def login(db: Session = Depends(get_db), login: str=Form(), password: str=Form()):
    user = users_repository.get_user_by_username(username=login)
    if user is None:
        return Response(
            content=b"User not found\n",
            media_type="text/plain",
            status_code=404
        )

    if user.password != password:
        return Response(
            content=b"Incorrect password\n",
            media_type="text/plain",
            status_code=401
        )

    response = Response(status_code=200)
    token = encode_jwt(user_id=user.id)
    response.set_cookie("token", token)
    return response
