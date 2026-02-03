from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./history.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class CheckLog(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    risk = Column(Float)
    categories = Column(String)
    highlights = Column(String)
    rewrites = Column(String)


def init_db():
    Base.metadata.create_all(bind=engine)
