from operator import isub

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
import html

from app.bot.keyboards import get_main_keyboard, unsubscribe_keyboard, subscribe_keyboard, get_region_keyboard, get_news_keyboard
from app.database.crud import register_user, check_status, subscribe

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await register_user(telegram_id=message.from_user.id)
    welcome_text = (
        "👋 <b>👋 Hi! I'm your personal news assistant.</b>\n\n"
        "I collect the most important events, and my built-in AI analyzes them and creates short, understandable summaries.\n\n"
        "👇 Choose an action:"
    )
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="HTML")
@router.callback_query(F.data == "subscribe_status")
async def subscribe_status(callback: CallbackQuery):
    status = await check_status(telegram_id=callback.from_user.id)
    text = f"📊 <b>Subscription Status</b>\n\n• <b>Status:</b> {'🟢 Active' if status else '🔴 Inactive'}"
    markup = unsubscribe_keyboard() if status else subscribe_keyboard()
    await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "subscribe")
async def process_subscribe(callback: CallbackQuery):
    await subscribe(telegram_id=callback.from_user.id, subscribe_status=True)
    await callback.answer("✅ Subscribed")
    await subscribe_status(callback)
    
@router.callback_query(F.data == "unsubscribe")
async def process_unsubscribe(callback: CallbackQuery):
    await subscribe(telegram_id=callback.from_user.id, subscribe_status=False)
    await callback.answer("❌ Unsubscribed")
    await subscribe_status(callback)

    
@router.callback_query(F.data == "back")
async def back_to_menu(callback: CallbackQuery):
    welcome_text = (
        "👋 <b>👋 Hi! I'm your personal news assistant.</b>\n\n"
        "I collect the most important events, and my built-in AI analyzes them and creates short, understandable summaries.\n\n"
        "👇 Choose an action:"
    )
    await callback.message.edit_text(welcome_text, reply_markup=get_main_keyboard(), parse_mode="HTML")
    await callback.answer()

    

    
    
