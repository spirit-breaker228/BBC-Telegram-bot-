import asyncio
import logging
from sqlalchemy import select, update
from pydantic import BaseModel, Field

from google import genai
from google.genai.types import GenerateContentConfig

from app.database.engine import SessionLocal
from app.database.models import News
from app.config import API_TOKEN



logger = logging.getLogger(__name__)

class FormattedNews(BaseModel):
    """
This Pydantic model defines the expected structure of the AI's response for formatted news. It includes fields for the title, summary, and analysis of the news item, all of which are required and must be strings. The model also provides descriptions for each field to clarify their intended content.
    """

    title: str = Field(
        description="Clickable, attractive headline of the news item in Ukrainian."
    )
    summary: str = Field(
        description="Short, clear description of the event in Ukrainian (2-3 sentences). No unnecessary water."
    )
    analysis: str = Field(
        description="General objective analysis of the situation, context or possible consequences of this event."
    )

async def process_unformatted_news():
    """
    This function retrieves unformatted news from the database, sends them to the AI for formatting, and updates the database with the formatted results.
    """
    logger.info("Searching for unformatted news")
    
    client = genai.Client(api_key=API_TOKEN)

    async with SessionLocal() as session:
        stmt = select(News.id, News.title, News.summary).where(News.is_formatted == False)
        result = await session.execute(stmt)
        unformatted_news = result.all()

    if not unformatted_news:
        logger.info("All news is formatted. No news to process.")
        return

    logger.info(f"Found {len(unformatted_news)} for processing.")

    for news_id, title, summary in unformatted_news:
        logger.info("Processing: %s...", title[:10])

        prompt = f"Original title: {title}\nOriginal text: {summary}"
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                response = await client.aio.models.generate_content(
                    model="gemini-3.6-flash", 
                    contents=f"""
                        Translate and format this news article. 
                        IMPORTANT: The total word count of the 'summary' and 'analysis' fields together must be exactly 80-100 words.
                        Write concisely, objectively, and to the point.
                        
                        News:
                        {prompt}
                    """,
                    config=GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=FormattedNews,
                        temperature=0.3,
                    ),
                )
                
                if not response or not response.parsed:
                    logger.warning(
                        "Gemini returned an empty response for news ID=%s, attempt=%s",
                        news_id,
                        attempt + 1
                    )
                    continue
                    
                ai_data = response.parsed
                
                async with SessionLocal() as write_session:
                    stmt = update(News).where(News.id == news_id).values(
                        formatted_title=ai_data.title,
                        formatted_summary=ai_data.summary,
                        formatted_analysis=ai_data.analysis,
                        is_formatted=True
                    )
                    await write_session.execute(stmt)
                    await write_session.commit()

                logger.info("Successfully formatted news ID=%s", news_id)
                break  
                
            except Exception:
                logger.exception(
                    "Error while processing news ID=%s, attempt=%s",
                    news_id,
                    attempt + 1
                )
                if attempt < max_retries - 1:
                    logger.warning("Retrying...")
                    await asyncio.sleep(5) 
                else:
                    logger.error("All attempts failed for news ID=%s. Skipping this news item.", news_id)
                    
    logger.info("All changes successfully saved to the database!")
