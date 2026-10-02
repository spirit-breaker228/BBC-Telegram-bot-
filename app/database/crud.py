from app.database.engine import SessionLocal
from sqlalchemy import select, func, update
from sqlalchemy.dialects.sqlite import insert
from app.database.models import News
from app.database.models import Users

async def save_news(news_list):
    if not news_list:
        return
    async with SessionLocal() as session:
   
        stmt = insert(News).values(news_list).on_conflict_do_nothing(index_elements=["bbc_news_ID"])
        await session.execute(stmt)
        await session.commit()

    """Region pagination"""

async def get_available_regions():
    async with SessionLocal() as session:
        stmt = select(News.location).where(News.is_formatted == True).distinct()
        result = await session.execute(stmt)
        return result.scalars().all()
    
async def get_news_by_region(location_name, page):
    async with SessionLocal() as session:
        stmt = select(News).where(News.is_formatted == True, News.location == location_name).order_by(News.published_date.desc()).limit(1).offset(page)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
async def count_news_by_region(location_name):
    async with SessionLocal() as session:
        stmt = select(func.count()).select_from(News).where(News.is_formatted== True, News.location == location_name).order_by(News.published_date.desc())
        result = await session.execute(stmt)
        return result.scalars().one()

    '''News Pagination'''

async def get_news_pagination(page: int):   
    async with SessionLocal() as session:
        stmt = select(News).where(News.is_formatted== True).order_by(News.published_date.desc()).limit(1).offset(page)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
async def count_news():
    async with SessionLocal() as session:
        stmt = select(func.count()).select_from(News).where(News.is_formatted== True).order_by(News.published_date.desc()).limit(1)
        result = await session.execute(stmt)
        return result.scalars().one()
    
    
    """Subscribe service"""

async def register_user(telegram_id):
    async with SessionLocal() as session:
        stmt = select(Users).where(Users.telegram_id  == telegram_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            return
        else:
            session.add(Users(telegram_id=telegram_id))
            await session.commit()

async def check_status(telegram_id):
    async with SessionLocal() as session:
        stmt = select(Users.is_subscribed).where(Users.telegram_id == telegram_id)
        result = await session.execute(stmt)
        user_status = result.scalar_one_or_none()
        return user_status
    
async def subscribe(telegram_id, subscribe_status):
    async with SessionLocal() as session:
        stmt = update(Users).where(Users.telegram_id == telegram_id).values(is_subscribed = subscribe_status)
        await session.execute(stmt)
        await session.commit()

async def subscribed_user():
    async with SessionLocal() as session:
        stmt = select(Users.telegram_id).where(Users.is_subscribed == True)
        result = await session.execute(stmt)
        return result.scalars().all()