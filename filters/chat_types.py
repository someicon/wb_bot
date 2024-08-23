from typing import Any
from aiogram import Bot
from aiogram.filters import Filter
from aiogram.types import Message

from credentials.admins import admins_list


class ChatTypesFilter(Filter):
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types

    async def __call__(self, message: Message) -> bool:
        return message.chat.type in self.chat_types


class IsAdmin():
    def __init__(self) -> None:
        pass

    def __call__(self, message: Message) -> Any:
        return message.from_user.id in admins_list
