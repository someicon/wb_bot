from ast import Str
from email.policy import strict
from tkinter.tix import Tree
from sqlalchemy import DateTime, String, Text, func, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    created: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    user_name: Mapped[str] = mapped_column(String(50))
    user_full_name: Mapped[str] = mapped_column(String(150))
    status: Mapped[str] = mapped_column(String(50))
    image: Mapped[str] = mapped_column(String(150))
    text_message: Mapped[str] = mapped_column(String(150))


class TestUser(Base):
    __tablename__ = 'test_user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(String(150))
