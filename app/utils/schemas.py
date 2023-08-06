from pydantic import BaseModel
from .database import Base


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


class UserProfileEdit(BaseModel):
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


class AdEdit(BaseModel):
    type: str
    price: int
    address: str
    area: float
    rooms_count: int
    description: str


class CommentCreateRequest(BaseModel):
    content: str


class CommentEdit(BaseModel):
    content: str
