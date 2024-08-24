import asyncio
import os
import logging

from dotenv import load_dotenv
from aiogram.client import default
from aiogram.enums import ParseMode
from aiogram import Dispatcher, Bot

from credentials.admins import admins_list
from handlers.user_private import user_private_router
from handlers.admin_private import admin_private_router


load_dotenv()


bot = Bot(
    token=os.getenv("TOKEN"),
    default=default.DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

ALLOWED_UPDATES = ["Message", "CallbackQuery"]


async def start_bot(bot: Bot):

    logging.info("Бот запущен")
    for admin in admins_list:
        try:
            await bot.send_message(admin, text="Бот запущен")
        except Exception as e:
            logging.error(
                f"Не удалось отправить сообщение админу {admin}: {e}")
        else:
            logging.info(
                f"сообщение отправлено админу {admin}")


async def stop_bot(bot: Bot):
    for admin in admins_list:
        try:
            await bot.send_message(admin, text="Остановлен")
        except Exception as e:
            logging.error(
                f"Не удалось отправить сообщение админу {admin}: {e}")
        else:
            logging.info(f"сообщение отправлено админу {admin}")


async def main():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    dp.include_routers(user_private_router, admin_private_router)

    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен")
