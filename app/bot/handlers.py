from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from app.bot.keyboards import get_main_keyboard
from app.database.crud import get_latest_formatted_news

from app.services.async_parser import run_parser 
from app.services.ai_formatter import process_unformatted_news 

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    welcome_text = (
        "👋 <b>👋 Hi! I'm your personal news assistant.</b>\n\n"
        "I collect the most important events, and my built-in AI analyzes them and creates short, understandable summaries.\n\n"
        "👇 Choose an action:"
    )
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="HTML")

# @router.message(Command("news"))
# async def trigger_parsing(message: Message):
#     """
#     This command sequentially triggers the collection of raw data and then their formatting by the AI.
#     """
#     await message.answer("🔄 1/2 Starting to collect raw news from the website...")
#     await run_parser() # Collects and saves to DB (is_formatted=False)
    
#     await message.answer("🧠 2/2 Sending news to AI for formatting...")
#     await process_unformatted_news() # Reads from DB, formats, updates DB (is_formatted=True)[cite: 1, 4]
    
#     await message.answer("✅ Database successfully updated! You can now press the 'Latest News' button in /start.")


@router.callback_query(F.data == "get_latest_news")
async def send_latest_news(callback: CallbackQuery):
    news = await get_latest_formatted_news()
    
    if not news:
        await callback.answer("There are currently no formatted news in the database. Please type /news", show_alert=True)
        return
    
    # Використовуємо відформатовані дані від ШІ[cite: 4]
    title = news.formatted_title or news.title
    summary = news.formatted_summary or news.summary
    analysis = news.formatted_analysis or "No analysis available."
    time = news.published_date.strftime("%Y-%m-%d %H:%M:%S") if news.published_date else "Unknown time"
    location = news.location or "No category"
    text = f"🗞 <b>{title}</b>\n\n📝 {summary}\n\n📊 {analysis}\n\n📍 <i>{location}</i>\n\n⏰ <i>{time}</i>"
    
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "subscribe")
async def process_subscribe(callback: CallbackQuery):
    await callback.answer("✅ You have subscribed! (Subscription feature in development)", show_alert=True)