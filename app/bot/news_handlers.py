import html
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
import html

from app.bot.keyboards import get_news_keyboard, get_region_keyboard,get_regions_pagination,get_main_keyboard,NewsPaginatorCallback, RegionNewsCallback
from app.database.crud import get_news_pagination, count_news, get_available_regions, get_news_by_region, count_news_by_region

news_router = Router()


def single_slide(news_item):
    title = html.escape(news_item.formatted_title or news_item.title or "Без назви")
    summary = html.escape(news_item.formatted_summary or news_item.summary or "")
    analysis = html.escape(news_item.formatted_analysis or "")
    time = html.escape(
        news_item.published_date.strftime("%Y-%m-%d %H:%M:%S UTC")
        if news_item.published_date
        else "Unknown time"
    )
    location = html.escape(news_item.location or "No category")
    return f"🗞 <b>{title}</b>\n\n📝 {summary}\n\n📊 {analysis}\n\n📍 <i>{location}</i>\n\n⏰ <i>{time}</i>\n\n"

async def markup_for_pagination(callback: CallbackQuery ,page):
    news = await get_news_pagination(page)
    total = await count_news()
    if not news:
        await callback.answer("⚠️ No news available")
    text = single_slide(news)
    markup = get_news_keyboard(current_page=page, totals=total)
    await callback.message.edit_text(
        text=text,
        reply_markup=markup,
        parse_mode="HTML"
    )
@news_router.callback_query(F.data == "get_latest_news")
async def first_news_slide(callback: CallbackQuery):
    await markup_for_pagination(callback, page = 0)

@news_router.callback_query(NewsPaginatorCallback.filter())
async def procces_pagination(callback:CallbackQuery, callback_data:NewsPaginatorCallback):
    await markup_for_pagination(callback, page = callback_data.page)

@news_router.callback_query(F.data == "ignore")
async def ignore_click(callback: CallbackQuery):
    await callback.answer()

"""Regions Pagination"""
@news_router.callback_query(F.data == "back_to_regions")
@news_router.callback_query(F.data == "open_regions_menu")
async def inline_show_regions(callback: CallbackQuery):
    regions_list = await get_available_regions()
    await callback.message.edit_text(
        "🌍 Choose a region:",
        reply_markup=get_region_keyboard(available_regions = regions_list)
    )
    await callback.answer()

@news_router.callback_query(RegionNewsCallback.filter())
async def get_news_pagination_by_region(callback: CallbackQuery, callback_data: RegionNewsCallback):
    region = callback_data.region
    page = callback_data.page
    news = await get_news_by_region(location_name=region, page=page)
    total = await count_news_by_region(location_name=region)
    if not news:
        await callback.answer("⚠️ No news available for this region.", show_alert=True)
        return 
    text =single_slide(news)
    markup = get_regions_pagination(region= region, page=page, totals=total)
    try:
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=markup)
    except Exception as e:
        await callback.answer(f"Error: {str(e)}", show_alert=True)


     