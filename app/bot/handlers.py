from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
import html

from app.bot.keyboards import get_main_keyboard, get_subscribe_keyboard
from app.database.crud import get_latest_formatted_news, register_or_update_user

from app.services.async_parser import run_parser 
from app.services.ai_formatter import process_unformatted_news 

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await register_or_update_user(telegram_id=message.from_user.id, subscribed=False)
    welcome_text = (
        "👋 <b>👋 Hi! I'm your personal news assistant.</b>\n\n"
        "I collect the most important events, and my built-in AI analyzes them and creates short, understandable summaries.\n\n"
        "👇 Choose an action:"
    )
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="HTML")

@router.callback_query(F.data == "get_latest_news")
async def send_latest_news(callback: CallbackQuery):
    news = await get_latest_formatted_news()
    
    if not news:
        await callback.answer("There are currently no formatted news in the database. Please type /news", show_alert=True)
        return
    
    # Використовуємо відформатовані дані від ШІ[cite: 4]
    title = html.escape(news.formatted_title or news.title or "Без назви")
    summary = html.escape(news.formatted_summary or news.summary or "")
    analysis = html.escape(news.formatted_analysis or "")
    time = html.escape(news.published_date.strftime("%Y-%m-%d %H:%M:%S") if news.published_date else "Unknown time")
    location = html.escape(news.location or "No category")
    text = f"🗞 <b>{title}</b>\n\n📝 {summary}\n\n📊 {analysis}\n\n📍 <i>{location}</i>\n\n⏰ <i>{time}</i>"
    
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "subscribe")
async def process_subscribe(callback: CallbackQuery):
    await register_or_update_user(telegram_id=callback.from_user.id, subscribed=True)
    await callback.message.edit_reply_markup(reply_markup=get_subscribe_keyboard())
    await callback.answer("✅ You have subscribed! (Subscription feature in development)", show_alert=True)
    

@router.callback_query(F.data == "unsubscribe")
async def process_unsubscribe(callback: CallbackQuery):
    await register_or_update_user(telegram_id=callback.from_user.id, subscribed=False)
    await callback.message.edit_reply_markup(reply_markup=get_main_keyboard())
    await callback.answer("✅ You have unsubscribed!", show_alert=True)