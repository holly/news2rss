from .category import Category
from .service import Service
from .item import Item

def create_tables():
    from setting import Engine, Base
    Base.metadata.create_all(bind=Engine)
