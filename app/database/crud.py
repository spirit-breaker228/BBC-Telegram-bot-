from app.database.engine import SessionLocal
from sqlalchemy import select
from app.database.models import News


async def save_news(news_list):
    async with SessionLocal() as session:
        for item in news_list:
            smnt = select(News).where(News.title == item["Title"])
            result = await session.execute(smnt)
            existing_news = result.scalar_one_or_none()
            if existing_news:
                continue
            news = News(
                title=item["Title"],
                summary=item["Sum"],
                location=item["Location"],
                published_date=item["published_date"],
            )
            session.add(news)
        await session.commit()

async def get_latest_formatted_news():
    async with SessionLocal() as session:
        stmt = (
            select(News)
            .where(News.is_formatted == True)
            .order_by(News.published_date.desc())
            .limit(1)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()