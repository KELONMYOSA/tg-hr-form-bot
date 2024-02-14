import asyncio
import logging

from aiogram import Bot, Dispatcher

from src import handlers
from src.config import settings


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(handlers.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
