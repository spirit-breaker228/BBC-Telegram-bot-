import asyncio
from curl_cffi import AsyncSession
from app.database.crud import save_news
from datetime import datetime

async def fetch_page(session, page, url, headers):
    """
    Fetches a single page of news data from the BBC API.
    """
    params = {
        "country": "ua",
        "page": f"{page}",
        "size": "9",
        "path": "/news/world",
    }
    response = await session.get(url, params=params, headers=headers)

    response.raise_for_status()

    data = response.json()
    news = data.get("data", [])
    page_data = []
    for item in news:
        news_title = item.get("title")
        news_sum = item.get("summary")
        if not news_title or not news_sum:
            continue  # Skip if title or summary is missing
        topics = item.get("topics") or []

        news_location = topics[0] if topics else "Без категорії"

        news_time = item.get("lastPublishedAt")

        news_time = item.get("lastPublishedAt")
        if news_time:
            date_str = news_time.split("T")[0]
            published_date = datetime.strptime(date_str, "%Y-%m-%d")
        else:
            published_date = datetime.now()
        page_data.append(
            {
                "Title": news_title,
                "Sum": news_sum,
                "Location": news_location,
                "published_date": published_date,
            }
        )
    return page_data


async def get_news(
    referer="https://www.bbc.com/news/world",
    url="https://web-cdn.api.bbci.co.uk/xd/content-collection/07cedf01-f642-4b92-821f-d7b324b8ba73",
):
    """
    Fetches news data from the BBC API and returns a list of news items.
    """
    headers = {
        "sec-ch-ua-platform": '"Windows"',
        "Referer": referer,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
        "sec-ch-ua-mobile": "?0",
    }
    async with AsyncSession(impersonate="chrome124") as session:
        tasks = []
        for page in range(2):
            task = fetch_page(
                session,
                page,
                url,
                headers,
            )

            tasks.append(task)

        result = await asyncio.gather(*tasks)
        all_data = []
        for page in result:

            all_data.extend(page)
        return all_data


async def run_parser():
    """
    Runs the news parser and saves the collected news data to the database.
    """
    news_data = await get_news()
    print(f"Collected {len(news_data)}.")

    await save_news(news_data)
    print("Done")
