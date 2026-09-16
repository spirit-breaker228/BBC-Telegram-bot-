import html
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
import html

from app.bot.keyboards import get_main_keyboard, get_subscribe_keyboard, get_news_keyboard, NewsPaginatorCallback
from app.database.crud import get_latest_formatted_news, register_or_update_user, get_latest_5_formatted_news

news_router = Router()


def single_slide(news_item, index, total):
    title = html.escape(news_item.formatted_title or news_item.title or "Без назви")
    summary = html.escape(news_item.formatted_summary or news_item.summary or "")
    analysis = html.escape(news_item.formatted_analysis or "")
    time = html.escape(
        news_item.published_date.strftime("%Y-%m-%d %H:%M:%S")
        if news_item.published_date
        else "Unknown time"
    )
    location = html.escape(news_item.location or "No category")
    return f"🗞 <b>{title}</b>\n\n📝 {summary}\n\n📊 {analysis}\n\n📍 <i>{location}</i>\n\n⏰ <i>{time}</i>"

@news_router.callback_query(F.data == "get_latest_news")
async def show_latest_news(callback: CallbackQuery):
    news_list = await get_latest_5_formatted_news()
    if not news_list:
        await callback.answer("⚠️ Немає доступних новин.")
        return

    text = single_slide(news_list[0], 0, len(news_list))
    markup = get_news_keyboard(current_page=0, totals=len(news_list))
    await callback.message.answer(text=text, reply_markup=markup, parse_mode="HTML")
    await callback.answer()  
@news_router.callback_query(NewsPaginatorCallback.filter())

async def process_news_pagination(callback: CallbackQuery, callback_data: NewsPaginatorCallback):
    news_list = await get_latest_5_formatted_news()
    page = callback_data.page
    if page < 0 or page >= len(news_list):
        await callback.answer("Invalid page number.", show_alert=True)
        return
    text = single_slide(news_list[page], page, len(news_list))
    markup = get_news_keyboard(current_page=page, totals=len(news_list))
    try:
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=markup)
    except Exception as e:
        await callback.answer(f"Error: {str(e)}", show_alert=True)
        
@news_router.callback_query(F.data == "ignore")
async def ignore_click(callback: CallbackQuery):
    await callback.answer()