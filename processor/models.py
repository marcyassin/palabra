# processor/models.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Book:
    id: int
    title: str
    filename: str       # The filename in MinIO
    language: str
    user_id: Optional[int]
    status: str         # 'pending', 'processing', 'done'
    created: datetime
    processed: Optional[datetime] = None


@dataclass
class Word:
    id: int
    word: str
    language: str
    difficulty: int     # 1-6 for now (A1-C2)
    frequency: int
    created: datetime


@dataclass
class BookWord:
    id: int
    book_id: int
    word_id: int
    frequency: int
