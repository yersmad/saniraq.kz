from attrs import define
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import Session

from .database import Base


class Ad(Base):
    __tablename__ = "ads"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    price = Column(Integer)
    address = Column(String)
    area = Column(Float)
    rooms_count = Column(Integer)
    description = Column(String)


@define
class AdCreate:
    type: str
    price: int
    address: str
    area: float
    rooms_count: int
    description: str


class AdsRepository:
    def get_ad(self, db: Session, ad_id: int) -> Ad | None:
        return db.query(Ad).filter(Ad.id == ad_id).first()

    def get_ad_by_address(self, db: Session, address: str) -> Ad | None:
        return db.query(Ad).filter(Ad.address == address).first()

    def get_ads(self, db: Session, skip: int = 0, limit: int = 100) -> list[Ad]:
        return db.query(Ad).offset(skip).limit(limit).all()

    def create_ad(self, db: Session, ad: AdCreate) -> Ad:
        db_ad = Ad(
            type=ad.type, 
            price=ad.price, 
            address=ad.address, 
            area=ad.area, 
            rooms_count=ad.rooms_count, 
            description=ad.description
        )
        db.add(db_ad)
        db.commit()
        db.refresh(db_ad)
        return db_ad

    def update_ad(self, db: Session, ad_id: int, new_data: Ad) -> Ad:
        db_ad = db.query(Ad).filter(Ad.id == ad_id).update({
            Ad.type: new_data.type, 
            Ad.price: new_data.price, 
            Ad.address: new_data.address,
            Ad.area: new_data.area,
            Ad.rooms_count: new_data.rooms_count,
            Ad.description: new_data.description
        })
        db.commit()
        db.refresh()

    def delete_ad_by_id(self, db: Session, ad_id: int):
        db_ad = db.query(Ad).filter(Ad.id == Ad_id).delete()
        db.commit()
        db.refresh()
