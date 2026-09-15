from aiogram import Router
from aiogram.filters import BaseFilter, Command
from aiogram.types import Message, CallbackQuery
from typing import Union

from app.services.async_parser import run_parser 
from app.services.ai_formatter import process_unformatted_news 

from app.config import ADMIN_CHAT_ID
ADMIN_IDS = ADMIN_CHAT_ID  
admin_router = Router()

class IsAdminFilter(BaseFilter):
    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        is_admin = (event.from_user.id == ADMIN_IDS)
        return is_admin
    
@admin_router.message(Command("newss"), IsAdminFilter()) 
async def trigger_parsing(message: Message):
    """
    This command sequentially triggers the collection of raw data and then their formatting by the AI.
    """
    await message.answer("🔄 1/2 Starting to collect raw news from the website...")
    await run_parser() # Collects and saves to DB (is_formatted=False)
        
    await message.answer("🧠 2/2 Sending news to AI for formatting...")
    await process_unformatted_news() # Reads from DB, formats, updates DB (is_formatted=True)[cite: 1, 4]
        
    await message.answer("✅ Database successfully updated! You can now press the 'Latest News' button in /start.")