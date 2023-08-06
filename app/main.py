from fastapi import FastAPI, Response, Depends, HTTPException, Form, Cookie, Request
from fastapi.responses import RedirectResponse, ORJSONResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime
from typing import Optional

from .utils.ads_repository import Ad, AdsRepository, AdCreate
from .utils.users_repository import User, UsersRepository, UserCreate
from .utils.comments_repository import Comment, CommentsRepository, CommentCreate
from .utils.database import Base, engine, SessionLocal
from .utils.schemas import UserCreateRequest, UserProfileResponse, UserProfileEdit, AdCreateRequest, AdResponse, AdEdit, CommentCreateRequest, CommentEdit


Base.metadata.create_all(bind=engine)

app = FastAPI()

users_repository = UsersRepository()
ads_repository = AdsRepository()
comments_repository = CommentsRepository()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/users/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def encode_jwt(username: str) -> dict:
    body = {"username": username}
    token = jwt.encode(body, "test", 'HS256')
    dict_token = {"token": token}
    return dict_token["token"]


def decode_jwt(token: dict):
    data = jwt.decode(token, "test", 'HS256')
    return data["username"]


@app.post("/auth/users")
def signup(
    input: UserCreateRequest, 
    db: Session = Depends(get_db)
):
    db_user = users_repository.get_user_by_username(db=db, username=input.username)
    if db_user != None:
        raise HTTPException(status_code=403, detail="User is already exists")

    created_user = users_repository.create_user(db=db, user=UserCreate(
        username=input.username,
        phone=input.phone,
        password=input.password,
        name=input.name,
        city=input.city
    ))

    return Response(status_code=200)


@app.post("/auth/users/login")
def login(
    username: str=Form(),
    password: str=Form(),
    db: Session = Depends(get_db),
):
    user = users_repository.get_user_by_username(db=db, username=username)
    if not user:
        raise HTTPException(status_code=404, detail="User is not found")

    if user.password != password:
        raise HTTPException(status_code=401, detail="Incorrect password")

    token = encode_jwt(username=username)
    return {"access_token": token}


# def get_current_user(
#     db: Session=Depends(get_db),
#     token: str=Depends(oauth2_scheme)
# ):
#     decoded_username = decode_jwt(token=token)
#     user = users_repository.get_user_by_username(db=db, username=str(decoded_username))

#     if not str(decoded_username):
#         raise HTTPException(status_code=400, detail="Invalid token")
    
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     return user


@app.patch("/auth/users/me")
def edit_profile(
    input: UserProfileEdit,
    db: Session=Depends(get_db),
    token: str=Depends(oauth2_scheme), 
):
    decode_username = decode_jwt(token=token)
    user = users_repository.get_user_by_username(db=db, username=decode_username)
    edited_user = users_repository.update_user(db=db, prev_user=user, new_user=input)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return Response(status_code=200)


@app.get("/auth/users/me")
def show_profile(
    db: Session=Depends(get_db), 
    token: str=Depends(oauth2_scheme)
):
    decode_username = decode_jwt(token=token)
    user = users_repository.get_user_by_username(db=db, username=decode_username)
    return {
        "id": user.id,
        "username":user.username,
        "phone": user.phone,
        "name": user.name,
        "city": user.city
    }


@app.post("/shanyraks")
def create_ad(
    input: AdCreateRequest,
    db: Session=Depends(get_db),
    token: str=Depends(oauth2_scheme)
):
    decode_username = decode_jwt(token=token)
    db_ad = ads_repository.get_ad_by_address(db=db, address=input.address)
    db_user = users_repository.get_user_by_username(db=db, username=decode_username)

    if db_ad:
        raise HTTPException(status_code=403, detail="Advertisement is already exists")

    created_ad = ads_repository.create_ad(db=db, ad=AdCreate(
        type=input.type,
        price=input.price,
        address=input.address,
        area=input.area,
        rooms_count=input.rooms_count,
        description=input.description,
        owner_id=db_user.id
    ))

    return {"id": created_ad.id}


@app.get("/shanyraks/{id}")
def get_ad(
    id: int,
    db: Session=Depends(get_db),
    token: str=Depends(oauth2_scheme)
):
    db_ad = ads_repository.get_ad_by_id(db=db, ad_id=id)

    if not db_ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    
    return {
        "id": db_ad.id,
        "type": db_ad.type,
        "price": db_ad.price,
        "address": db_ad.address,
        "area": db_ad.address,
        "rooms_count": db_ad.rooms_count,
        "description": db_ad.description,
        "user_id": db_ad.owner_id
    }


@app.patch("/shanyraks/{id}")
def edit_ad(
    id: int,
    input: AdEdit,
    db: Session=Depends(get_db),
    token: str=Depends(oauth2_scheme)
):
    decode_username = decode_jwt(token=token)
    db_ad = ads_repository.get_ad_by_id(db=db, ad_id=id)
    current_user = users_repository.get_user_by_username(db=db, username=decode_username)

    if not db_ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")

    if current_user.id != db_ad.owner_id:
        raise HTTPException(status_code=403, detail="Has no rights")

    edited_ad = ads_repository.update_ad(db=db, ad_id=id, new_data=input)

    return Response(status_code=200)


@app.delete("/shanyraks/{id}")
def delete_ad(
    id: int,
    db: Session=Depends(get_db),
    token: str=Depends(oauth2_scheme)
):
    decode_username = decode_jwt(token=token)
    db_ad = ads_repository.get_ad_by_id(db=db, ad_id=id)
    current_user = users_repository.get_user_by_username(db=db, username=decode_username)


    if not db_ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")

    if current_user.id != db_ad.owner_id:
        raise HTTPException(status_code=403, detail="Has no rights")

    deleted_ad = ads_repository.delete_ad_by_id(db=db, ad_id=id)

    return Response(status_code=200)


@app.post("/shanyraks/{id}/comments")
def create_comment(
    input: CommentCreateRequest,
    id: int,
    db: Session=Depends(get_db),
    token: str=Depends(oauth2_scheme)
):
    decode_username = decode_jwt(token=token)
    db_comment = comments_repository.get_comment_by_content(db=db, content=input.content)
    db_user = users_repository.get_user_by_username(db=db, username=decode_username)

    if db_comment:
        raise HTTPException(status_code=403, detail="Comment is already exists")

    created_comment = comments_repository.create_comment(db=db, comment=CommentCreate(
        content=input.content,
        created_at=str(datetime.now()),
        edited=False,
        owner_id=db_user.id,
        ad_id=id
    ))

    return Response(status_code=200)


@app.get("/shanyraks/{id}/comments")
def show_comments(
    id: int,
    db: Session=Depends(get_db),
    token: str=Depends(oauth2_scheme)
):
    db_ad = ads_repository.get_ad_by_id(db=db, ad_id=id)
    db_comments = comments_repository.get_comments_by_ad_id(db=db, ad_id=id)

    if not db_ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")

    if not db_comments:
        raise HTTPException(status_code=404, detail="No comments")

    return {"comments": db_comments}
    

@app.patch("/shanyraks/{id}/comments/{comment_id}")
def edit_comment(
    id: int,
    comment_id:int,
    input: CommentEdit,
    db: Session=Depends(get_db),
    token: str=Depends(oauth2_scheme)
):
    decode_username = decode_jwt(token=token)
    db_ad = ads_repository.get_ad_by_id(db=db, ad_id=id)
    db_comment = comments_repository.get_comment_by_id(db=db, comment_id=comment_id)
    current_user = users_repository.get_user_by_username(db=db, username=decode_username)

    if not db_ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")

    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if current_user.id != db_comment.owner_id:
        raise HTTPException(status_code=403, detail="Has no rights")

    edited_comment = comments_repository.update_comment(db=db, comment_id=comment_id, new_data=input)

    return Response(status_code=200)


@app.delete("/shanyraks/{id}/comments/{comment_id}")
def delete_comment(
    id: int,
    comment_id: int,
    db: Session=Depends(get_db),
    token: str=Depends(oauth2_scheme)
):
    decode_username = decode_jwt(token=token)
    db_ad = ads_repository.get_ad_by_id(db=db, ad_id=id)
    db_comment = comments_repository.get_comment_by_id(db=db, comment_id=comment_id)
    current_user = users_repository.get_user_by_username(db=db, username=decode_username)

    if not db_ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")

    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if current_user.id == db_comment.owner_id or current_user.id == db_ad.owner_id:
        delete_comment = comments_repository.delete_comment_by_id(db=db, comment_id=comment_id)
        return Response(status_code=200)

    raise HTTPException(status_code=403, detail="Has no rights")


@app.post("/auth/users/favorites/shanyraks/{id}")
def add_to_favorite(
    id: int,
    db: Session=Depends(get_db),
    token: str=Depends(oauth2_scheme)
):
    favorites = ads_repository.add_to_favorite_list(db=db, ad_id=id)

    return Response(status_code=200)


@app.get("/auth/users/favorites/shanyraks")
def get_favorites(
    db: Session=Depends(get_db),
    token: str=Depends(oauth2_scheme)
):
    return {"shanyraks": ads_repository.get_all_favorites()}


@app.delete("/auth/users/favorites/shanyraks/{id}")
def delete_from_favorites(
    id: int,
    db: Session=Depends(get_db),
    token: str=Depends(oauth2_scheme)
):
    favorites = ads_repository.delete_favorite_ad_by_id(ad_id=id)

    return Response(status_code=200)


@app.get("/shanyraks")
def search(
    limit: int=10,
    offset: int=0,
    type: Optional[str] = None,
    rooms_count: Optional[int] = None,
    price_from: Optional[int] = None,
    price_until: Optional[int] = None,
    db: Session=Depends(get_db)
):
    objects = ads_repository.get_ads(db=db, skip=offset, limit=limit, type=type, rooms_count = rooms_count, price_from = price_from, price_until = price_until)

    return {
        "total": len(objects),
        "objects": objects
    }
