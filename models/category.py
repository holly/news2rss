import json
from sqlalchemy import Column, Integer, String, Text, DateTime,  ForeignKey, CheckConstraint, UniqueConstraint, create_engine, and_, or_, not_
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, relationship, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from setting import Engine, Session, Base

# 循環インポート回避の型チェック
if TYPE_CHECKING:
    from .category import Category

class Category(Base):
    __tablename__ = 'categories'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False, unique=True)
    created: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    updated: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    services: Mapped[List["Service"]] = relationship("Service", back_populates="category", cascade="all, delete-orphan", lazy="select")
    
    # 制約
    #__table_args__ = (
    #    UniqueConstraint('name', name='unique_name')
    #)

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name='{self.name}')>"

    def __str__(self) -> str:
        #return self.name
        pass

# 使用例
if __name__ == "__main__":
    # テーブル作成
    Base.metadata.create_all(bind=Engine)
