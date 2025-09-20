from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 接続先DBの設定
database = 'sqlite:///news2rss.db'

# Engine の作成
Engine = create_engine(
  database,
  # for mysql or postgres
  #encoding="utf-8",
  echo=False
)

# Sessionの作成
Session = scoped_session(
    sessionmaker(
        autocommit = False,
        autoflush = False,
        bind = Engine
    )
)

# modelで使用する
Base = declarative_base()
Base.query = Session.query_property()
