from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🗞 Latest News", callback_data="get_latest_news")],
            [InlineKeyboardButton(text="🔔 Subscribe to Newsletter", callback_data="subscribe")]
        ]
    )