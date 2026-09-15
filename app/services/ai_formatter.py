import asyncio
from sqlalchemy import select
from pydantic import BaseModel, Field

from google import genai
from google.genai.types import GenerateContentConfig

from app.database.engine import SessionLocal
from app.database.models import News
from app.config import API_TOKEN

# ==========================================
# 1. SETUP
# ==========================================

client = genai.Client(api_key=API_TOKEN)


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


# ==========================================
# 2. MAIN FUNCTION
# ==========================================


async def process_unformatted_news():
    """
    This function retrieves unformatted news from the database, sends them to the AI for formatting, and updates the database with the formatted results.
    """
    print("Searching for unformatted news")

    async with SessionLocal() as session:

        stmt = select(News).where(News.is_formatted == False).limit(6)
        result = await session.execute(stmt)
        unformatted_news = result.scalars().all()

        if not unformatted_news:
            print("All news is formatted. No news to process.")
            return

        print(f"Found {len(unformatted_news)} for processing.")

        for news_item in unformatted_news:
            print(f"Processing: {news_item.title[:10]}...")

            prompt = f"Original title: {news_item.title}\nOriginal text: {news_item.summary}"
            max_retries = 3
            for attempt in range(max_retries):
                try:
                  
                    response = await client.aio.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=f"""
                            Translate and format this news article. 
                            IMPORTANT: The total word count of the 'summary' and 'analysis' fields together must be exactly 80-100 words.
                            Write concisely, objectively, and to the point.
                            
                            Новина:
                            {prompt}
                        """,
                        config=GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=FormattedNews,
                            temperature=0.3,
                        ),
                    )

                    ai_data = response.parsed
                    news_item.formatted_title = ai_data.title
                    news_item.formatted_summary = ai_data.summary
                    news_item.formatted_analysis = ai_data.analysis
                    news_item.is_formatted = True  
                    print("✅ Success!")
                    await session.commit() 
                    await asyncio.sleep(5)  
                except Exception as e:
                    print(f"❌ Error processing news: {e}")
                    if attempt < max_retries - 1:
                        print("Retrying...")
                        await asyncio.sleep(8) 
                    else:
                        print("All attempts failed. Skipping this news item.")

        print("All changes successfully saved to the database!")
