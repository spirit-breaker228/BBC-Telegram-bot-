import asyncio
import logging
from aiogram import Bot, Dispatcher
from app.config import BOT_TOKEN
from app.bot.handlers import router
from app.bot.admin_hanglers import admin_router
from app.bot.news_hanglers import news_router
from app.database.engine import engine
from app.database.engine import Base


async def main():
    logging.basicConfig(level=logging.INFO)
   
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    dp.include_router(admin_router)
    dp.include_router(news_router)

    # Delete webhook and drop pending updates to ensure the bot starts fresh
    await bot.delete_webhook(drop_pending_updates=True)
    print("🤖 Start!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
