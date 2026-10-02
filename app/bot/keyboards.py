from typing import Optional

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder 
def get_main_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🗞 Latest News", callback_data="get_latest_news")],
            [InlineKeyboardButton(text="📩 Subscribe status", callback_data="subscribe_status")],
            [InlineKeyboardButton(text="🌍 Regions", callback_data="open_regions_menu")]
        ]
    )

def subscribe_keyboard():
        return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔔 Subscribe", callback_data="subscribe")],
            [InlineKeyboardButton(text="🔙 Back to menu", callback_data="back")],
        ]
    )
def unsubscribe_keyboard():
        return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Unsubscribe", callback_data="unsubscribe")],
            [InlineKeyboardButton(text="🔙 Back to menu", callback_data="back")],
        ]
    )
class NewsPaginatorCallback(CallbackData, prefix="news_page"):
    page: int

def get_news_keyboard(current_page: int, totals: int):
    builder = InlineKeyboardBuilder()
    prev_page = current_page - 1 if current_page > 0 else totals - 1
    next_page = current_page + 1 if current_page < totals - 1 else 0
    builder.button(
        text="⬅️ Previous", callback_data=NewsPaginatorCallback(page=prev_page).pack()
    )
    builder.button(
        text=f"Page {current_page + 1}/{totals}", callback_data="ignore"
    )
    builder.button(
        text="➡️ Next", callback_data=NewsPaginatorCallback(page=next_page).pack()
    )
    builder.adjust(3)  

    builder_back = InlineKeyboardBuilder()
    builder_back.button(text="🔙 Back to menu", callback_data="back")
    builder_back.adjust(1)
    builder.attach(builder_back)
    return builder.as_markup()



class RegionNewsCallback(CallbackData, prefix="reg_news"):
    page : int
    region : Optional[str] = None

def get_region_keyboard(available_regions):
    builder = InlineKeyboardBuilder()
    for reg in available_regions:
        builder.button(
            text= reg, callback_data = RegionNewsCallback(region= reg, page=0).pack()
        )
    builder.button(text="🔙 Back to menu", callback_data="back")
    builder.adjust(1)
    return builder.as_markup()


def get_regions_pagination(region, page: int = 0,  totals: int = 0):
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Previous", callback_data=RegionNewsCallback(region=region, page=page-1 if page > 0 else totals - 1).pack())
    builder.button(text=f"Page {page + 1}/{totals}", callback_data="ignore")
    builder.button(text="➡️ Next", callback_data=RegionNewsCallback(region=region, page=page+1 if page < totals - 1 else 0).pack())
    builder.adjust(3)
    builder_back = InlineKeyboardBuilder()
    builder_back.button(text="🔙 Back to regions", callback_data="back_to_regions")
    builder_back.adjust(1)
    builder.attach(builder_back)
    return builder.as_markup()
