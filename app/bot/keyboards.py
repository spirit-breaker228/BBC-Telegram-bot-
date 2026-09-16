from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder 
def get_main_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🗞 Latest News", callback_data="get_latest_news")],
            [InlineKeyboardButton(text="📩 Subscribe to Newsletter", callback_data="subscribe")]
        ]
    )
def get_subscribe_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📤 Unsubscribe from Newsletter", callback_data="unsubscribe")],
            [InlineKeyboardButton(text="🗞 Latest News", callback_data="get_latest_news")]
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