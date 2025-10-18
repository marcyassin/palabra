from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Word(Base):
    __tablename__ = "words"
    id = Column(Integer, primary_key=True)
    word = Column(String, nullable=False)
    language = Column(String, nullable=False)

class BookWord(Base):
    __tablename__ = "book_words"
    book_id = Column(Integer, primary_key=True)
    word_id = Column(Integer, ForeignKey("words.id"), primary_key=True)
    count = Column(Integer, nullable=False)
