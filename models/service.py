import json
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, CheckConstraint, UniqueConstraint, create_engine, and_, or_, not_
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, relationship, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from setting import Engine, Session, Base

# 循環インポート回避の型チェック
if TYPE_CHECKING:
    from .item import Item

class Service(Base):
    __tablename__ = 'services'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=True)
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id', onupdate='CASCADE', ondelete='CASCADE'))
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    identifier: Mapped[str] = mapped_column(String(256), nullable=False)
    executor: Mapped[str]  = mapped_column(String(256), nullable=False)
    news_url: Mapped[str]  = mapped_column(String(256), nullable=False)
    base_url: Mapped[str]  = mapped_column(String(256), nullable=True)
    selector: Mapped[str]  = mapped_column(Text, nullable=True)
    tags: Mapped[str]  = mapped_column(Text, nullable=True, default="[]")
    is_active: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    updated: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # 多対1の関係でcategoryと紐づく
    category: Mapped["Category"] = relationship(back_populates="services", lazy="select")
    # 1対多 リレーションシップ（型アノテーション付き）
    items: Mapped[List["Item"]] = relationship("Item", back_populates="service", cascade="all, delete-orphan", lazy="select")
    
    # 制約
    __table_args__ = (
        CheckConstraint("executor IN ('bs4', 'feedparser')", name='check_executor'),
        CheckConstraint("is_active IN (0, 1)", name='check_is_active'),
        UniqueConstraint('name', name='unique_name'),
        UniqueConstraint('identifier', name='unique_identifier')
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "executor": self.executor,
            "news_url": self.news_url,
            "base_url": self.base_url,
            "selector": self.selector,
            "tags": json.loads(self.tags),
            "is_active": self.is_active,
            "category_id": self.category_id,
            "category_name": self.category.name,
        }

    def __repr__(self) -> str:
        return f"<Service(id={self.id}, name='{self.name}', identifier='{self.identifier}', executor='{self.executor}')>"

    def __str__(self) -> str:
        return self.name
   
    @classmethod
    def get_all_services(cls):
        result = {}
        for service in Session.query(cls).filter(cls.is_active == 1):
            result[service.identifier] = service.to_dict()
        return result

# 使用例
if __name__ == "__main__":
    # テーブル作成
    Base.metadata.create_all(bind=Engine)
