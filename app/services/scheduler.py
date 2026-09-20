import asyncio
from aiogram import Bot
from app.database.crud import get_latest_5_formatted_news, get_user_subscription_status
from app.services.async_parser import run_parser
from app.services.ai_formatter import process_unformatted_news
from app.bot.keyboards import get_news_keyboard
from app.bot.news_handlers import single_slide

async def run_scheduler(bot):
    print("🕒 Scheduler started.")
    await run_parser()
    await process_unformatted_news()

    news_list = await get_latest_5_formatted_news()
    users = await get_user_subscription_status()
    if not news_list or not users:
        print("⚠️ No formatted news available or users to send to.")
        return

    text = single_slide(news_list[0], 0, len(news_list))
    markup = get_news_keyboard(current_page=0, totals=len(news_list))
    count = 0
    for user_id in users:
        try: 
            bot.send_message(chat_id=user_id, text=text, reply_markup=markup, parse_mode="HTML")
            count += 1
        except Exception as e:
            print(f"⚠️ Failed to send news to user {user_id}: {e}")
    print(f"✅ [Scheduler] ")