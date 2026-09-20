from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
import html

from app.bot.keyboards import get_main_keyboard, get_subscribe_keyboard, get_news_keyboard, NewsPaginatorCallback
from app.database.crud import get_latest_formatted_news, register_or_update_user, get_latest_5_formatted_news

router = Router()

@router.message(CommandStart())
@router.message(Command("menu"))
async def cmd_start(message: Message):
    await register_or_update_user(telegram_id=message.from_user.id, subscribed=False)
    welcome_text = (
        "👋 <b>👋 Hi! I'm your personal news assistant.</b>\n\n"
        "I collect the most important events, and my built-in AI analyzes them and creates short, understandable summaries.\n\n"
        "👇 Choose an action:"
    )
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="HTML")

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