from attrs import define
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Double
from sqlalchemy.orm import Session
from typing import Optional

from .database import Base
from .schemas import AdEdit, AdResponse


class Ad(Base):
    __tablename__ = "advertisements"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    price = Column(Integer)
    address = Column(String)
    area = Column(Double)
    rooms_count = Column(Integer)
    description = Column(String)
    owner_id = Column(Integer)


@define
class AdCreate:
    type: str
    price: int
    address: str
    area: float
    rooms_count: int
    description: str
    owner_id: int


class AdsRepository:
    def __init__(self):
        self.favorites = [{}]

    def get_ad_by_id(self, db: Session, ad_id: int) -> Ad | None:
        return db.query(Ad).filter(Ad.id == ad_id).first()

    def get_ad_by_address(self, db: Session, address: str) -> Ad | None:
        return db.query(Ad).filter(Ad.address == address).first()

    def get_ads(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100, 
        type: Optional[str] = None,
        rooms_count: Optional[int] = None,
        price_from: Optional[int] = None,
        price_until: Optional[int] = None
    ) -> list[AdResponse]:

        result = db.query(Ad).filter(
            type == None or Ad.type == type,
            rooms_count == None or Ad.rooms_count == rooms_count,
            price_from == None or Ad.price >= price_from,
            price_until == None or Ad.price <= price_until 
        ).offset(skip).limit(limit).all()

        return list(map(lambda ad: AdResponse(id = ad.id, type = ad.type, price = ad.price, address = ad.address, area = ad.area, rooms_count = ad.rooms_count), result))

    def create_ad(self, db: Session, ad: AdCreate) -> Ad:
        db_ad = Ad(
            type=ad.type, 
            price=ad.price, 
            address=ad.address, 
            area=ad.area, 
            rooms_count=ad.rooms_count, 
            description=ad.description,
            owner_id=ad.owner_id
        )
        db.add(db_ad)
        db.commit()
        db.refresh(db_ad)
        return db_ad

    def update_ad(self, db: Session, ad_id: int, new_data: AdEdit) -> Ad:
        db_ad = db.query(Ad).filter(Ad.id == ad_id).update({
            Ad.type: new_data.type, 
            Ad.price: new_data.price, 
            Ad.address: new_data.address,
            Ad.area: new_data.area,
            Ad.rooms_count: new_data.rooms_count,
            Ad.description: new_data.description
        })
        db.flush()
        db.commit()

    def delete_ad_by_id(self, db: Session, ad_id: int):
        db_ad = db.query(Ad).filter(Ad.id == ad_id).delete()
        db.flush()
        db.commit()

    def add_to_favorite_list(self, db: Session, ad_id: int):
        db_ad = db.query(Ad).filter(Ad.id == ad_id).first()
        self.favorites.append({"id": db_ad.id, "address": db_ad.address})
    
    def get_all_favorites(self):
        return self.favorites

    def delete_favorite_ad_by_id(self, ad_id: int):
        for i, shanyrak in enumerate(self.favorites):
            if shanyrak["id"] == id:
                del self.favorites[i]
