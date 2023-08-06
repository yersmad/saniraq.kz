from attrs import define
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Double, DateTime
from sqlalchemy.orm import Session

from .database import Base
from .schemas import CommentEdit


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    created_at = Column(DateTime)
    edited = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    ad_id = Column(Integer, ForeignKey("advertisements.id"))


@define
class CommentCreate:
    content: str
    created_at: int
    edited: bool
    owner_id: int
    ad_id: int


class CommentsRepository:
    def get_comment_by_id(self, db: Session, comment_id: int) -> Comment | None:
        return db.query(Comment).filter(Comment.id == comment_id).first()

    def get_comments_by_ad_id(self, db: Session, ad_id:int) -> list[Comment] | None:
        return db.query(Comment).filter(Comment.ad_id == ad_id).all()

    def get_comment_by_content(self, db: Session, content: str) -> Comment | None:
        return db.query(Comment).filter(Comment.content == content).first()

    def get_comments(self, db: Session, skip: int = 0, limit: int = 100) -> list[Comment]:
        return db.query(Comment).offset(skip).limit(limit).all()

    def create_comment(self, db: Session, comment: CommentCreate) -> Comment:
        db_comment = Comment(
            content=comment.content,
            owner_id=comment.owner_id,
            ad_id=comment.ad_id
        )
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return db_comment

    def update_comment(self, db: Session, comment_id: int, new_data: CommentEdit) -> Comment:
        db_comment = db.query(Comment).filter(Comment.id == comment_id).update({Comment.content: new_data.content, Comment.edited: True})
        db.flush()
        db.commit()

    def delete_comment_by_id(self, db: Session, comment_id: int):
        db_comment = db.query(Comment).filter(Comment.id == comment_id).delete()
        db.flush()
        db.commit()
