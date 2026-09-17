from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder 
def get_main_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🗞 Latest News", callback_data="get_latest_news")],
            [InlineKeyboardButton(text="📩 Subscribe to Newsletter", callback_data="subscribe")],
            [InlineKeyboardButton(text="🌍 Regions", callback_data="open_regions_menu")]
        ]
    )
def get_subscribe_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📤 Unsubscribe from Newsletter", callback_data="unsubscribe")],
            [InlineKeyboardButton(text="🗞 Latest News", callback_data="get_latest_news")],
            [InlineKeyboardButton(text="🌍 Regions", callback_data="open_regions_menu")]
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
    builder.adjust(3)  # Adjust buttons to be in a single row
    return builder.as_markup()

class RegionNewsCallback(CallbackData, prefix="reg_news"):
    page : int
    region : str

def get_region_keyboard(region_name: str = None, page: int = 0, totals: int = 0):
    builder = InlineKeyboardBuilder()
    regions = ["Europe", "Middle East", "Asia", "US & Canada", "Africa"]

    for reg in regions:
        builder.button(
            text= reg, callback_data = RegionNewsCallback(region= reg, page = 0).pack()
        )
        builder.adjust(1)
        return builder.as_markup()