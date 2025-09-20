from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, create_engine, and_, or_, not_
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from setting import Engine, Session, Base

if TYPE_CHECKING:
    from .service import Service


class Item(Base):
    __tablename__ = 'items'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    service_id: Mapped[int] = mapped_column(ForeignKey('services.id',  onupdate='CASCADE', ondelete='CASCADE'))
    title: Mapped[str] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    link: Mapped[str] = mapped_column(Text)
    pubdate: Mapped[datetime] = mapped_column(DateTime)
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # リレーションシップ（型アノテーション付き）
    service: Mapped["Service"] = relationship("Service", back_populates="items", lazy="select")
    
    def __repr__(self) -> str:
        return f"<Item(id={self.id}, title='{self.title[:30]}...', service_id={self.service_id})>"

    def __str__(self) -> str:
        return self.title

    @classmethod
    def exists(cls, **kwargs):
        item =  Session.query(cls).filter(
            cls.service_id == kwargs["service_id"],
            cls.title      == kwargs["title"],
            cls.link       == kwargs["link"],
            cls.pubdate    == kwargs["pubdate"]
        ).first()
        return True if item else False

    @classmethod
    def bulk_insert(cls, items, check_duplicate=False):

        for data in items:
            if check_duplicate:
                if cls.exists(**data):
                    continue
            item = cls(**data)
            Session.add(item)
        Session.commit()

    @classmethod
    def get_items_by_service_id(cls, service_id, limit=10):

        return Session.query(cls).filter(
                    cls.service_id == service_id
                ).order_by(cls.pubdate.desc()).limit(limit).all()


# 使用例
if __name__ == "__main__":
    
    # テーブル作成
    Base.metadata.create_all(bind=Engine)
