from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True)
    word = Column(String, nullable=False)
    language = Column(String, nullable=False)
    difficulty = Column(Integer)
    zipf_score = Column(Float)
    created = Column(DateTime(timezone=False), server_default=func.now())


class BookWord(Base):
    __tablename__ = "book_words"

    book_id = Column(Integer, primary_key=True)
    word_id = Column(Integer, ForeignKey("words.id"), primary_key=True)
    count = Column(Integer, nullable=False)
