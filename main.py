import asyncio

from core import logger_activation
from database import Database
from telegram_handlers import launch_bot


async def main_task():
    await asyncio.gather(launch_bot())


if __name__=="__main__":
    db = Database()
    db.create_users_table()
    db.close()

    logger_activation()

    asyncio.run(main_task())
