# 📰 BBC News AI-Powered Telegram Bot & Automated Pipeline

An asynchronous Telegram bot and automated ETL pipeline for collecting BBC news, storing articles, processing them with Google Gemini AI, and delivering concise, structured news through an interactive Telegram interface.

Built with **Python**, **aiogram 3.x**, **SQLAlchemy 2.0 Async**, **APScheduler**, and **Google Gemini AI**.

---

## 📌 Overview

The project combines a Telegram bot with an automated news-processing pipeline.

The application periodically collects news from BBC, stores raw articles in a database, processes unformatted articles using Google Gemini AI, and makes the resulting content available through an interactive Telegram interface.

The system is organized into separate layers for:

- Telegram interaction
- Database access
- News parsing
- AI processing
- Background scheduling

## ✨ Features

### 📰 Async News Scraping
- Asynchronous BBC news collection.
- Extraction of article metadata.
- Storage of collected articles in the database.
- Processing of newly discovered articles without blocking the Telegram event loop.

### 🗄 Database Persistence
The application uses SQLAlchemy 2.0 Async for database access. Stored news contains information such as:
- original title;
- summary;
- geographical region;
- publication date;
- AI-generated title;
- AI-generated summary;
- AI-generated analysis;
- formatting status.

### 🔎 News Deduplication
Before inserting a new article, the application checks whether a corresponding news record already exists. The current deduplication approach uses the article title as the identifying value.

> **Note:** Title-based deduplication is suitable for the current project but is not a perfect article identity strategy. A stable article URL or source-specific article ID would be a stronger production solution.

### 🤖 AI Formatting & Analysis
Raw news articles are processed through Google Gemini AI. The AI processing layer generates structured content such as:
- improved title;
- concise summary;
- analytical breakdown.

The formatting process is separated from the parser so that news collection and AI processing remain independent components.

### 📄 Interactive Pagination
Users can browse processed news through Telegram inline keyboards. Pagination supports:
- previous article/page;
- next article/page;
- current page indicator;
- cyclic navigation.

Database queries use `LIMIT` and `OFFSET` instead of loading the complete dataset into memory.

### 🌍 Regional News
Users can select a geographical region and browse only news associated with that region. Regional pagination preserves both `region` and `page` inside Telegram callback data. This allows every callback to contain the information required to reconstruct the current navigation state.

### 👤 User Registration & Subscriptions
Users are registered when they interact with the bot. The database stores subscription status (`is_subscribed = True` / `is_subscribed = False`). Opening `/start` or `/menu` does not implicitly change the user's subscription state. Subscription is handled as a separate user action.

### ⏰ Automated Background Pipeline
APScheduler runs the news-processing workflow periodically:
```text
BBC Parser ──► Save new articles ──► AI Formatter ──► Formatted articles
```
This allows news processing to happen independently from user requests.

### 🔐 Admin Access
Administrative functionality is separated from normal user functionality. Admin operations can be restricted based on the configured administrator access logic.

---

## 🛠 Tech Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Language** | Python 3.10+ | Core application language |
| **Bot Framework** | aiogram 3.x | Telegram Bot API and asynchronous handlers |
| **ORM / Database** | SQLAlchemy 2.0 | ORM and database access |
| **Database Driver** | aiosqlite | Asynchronous SQLite access |
| **Scheduler** | APScheduler | Periodic background jobs |
| **AI Integration** | Google Gemini API | News summarization and analysis |
| **Async Runtime** | asyncio | Asynchronous application execution |
| **Configuration** | python-dotenv | Environment variable management |

---

## 🏗 Project Architecture

The application is divided into three primary areas:

```text
app/
├── bot/
├── database/
└── services/
```

### Bot Layer
Responsible for:
- Telegram commands;
- callback queries;
- user interaction;
- message rendering;
- inline keyboards;
- news navigation.

### Database Layer
Responsible for:
- SQLAlchemy engine;
- ORM models;
- database sessions;
- CRUD operations;
- pagination queries;
- region filtering;
- user persistence.

### Services Layer
Responsible for application-level operations outside the Telegram interface:
- BBC news parsing;
- AI formatting;
- scheduled processing.

---

## 📂 Project Structure

```text
bbc-project/
│
├── app/
│   │
│   ├── bot/
│   │   ├── admin_handlers.py    # Administrative Telegram handlers
│   │   ├── handlers.py          # Main bot commands and callbacks
│   │   ├── keyboards.py         # Inline keyboard builders
│   │   ├── main.py              # Application entry point
│   │   └── news_handlers.py     # News display and pagination handlers
│   │
│   ├── database/
│   │   ├── create_tables.py     # Database table initialization
│   │   ├── crud.py              # Database CRUD operations
│   │   ├── engine.py            # Async SQLAlchemy engine/session setup
│   │   └── models.py            # SQLAlchemy ORM models
│   │
│   ├── services/
│   │   ├── ai_formatter.py      # Gemini AI processing
│   │   ├── async_parser.py      # Asynchronous BBC news parser
│   │   └── scheduler.py         # Scheduled news-processing pipeline
│   │
│   └── config.py                # Application configuration
│
├── .env.example                 # Environment variable template
├── .gitignore
├── README.md
├── requirements.txt
└── ...
```

---

## 🗄 Database Schema

The application uses a relational database to persist news and users.

### `news`
The `news` table stores the complete lifecycle of collected articles.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | Integer | Primary key |
| `title` | String | Original headline collected from BBC |
| `summary` | Text | Original article summary |
| `location` | String | Geographic region associated with the article |
| `published_date` | DateTime | Article publication date |
| `formatted_title` | String | AI-generated title |
| `formatted_summary` | Text | AI-generated concise summary |
| `formatted_analysis`| Text | AI-generated analysis |
| `is_formatted` | Boolean | Whether AI processing has completed |

The `is_formatted` flag allows the scheduler to distinguish between:
```text
Raw article ──► is_formatted = False ──► AI processing ──► is_formatted = True
```

### `users`
The `users` table stores Telegram users and their subscription state.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | Integer | Internal primary key |
| `telegram_id` | BigInteger | Telegram user identifier |
| `is_subscribed` | Boolean | Subscription status |
| `created_at` | DateTime | User registration timestamp |

---

## ⚡ Automated Data Pipeline

1. **Extraction:** The parser collects news from BBC sources (`run_parser()`) and passes structured data to the database layer.
2. **Loading Raw Data:** Checks whether an article already exists before inserting (`is_formatted = False`).
3. **AI Transformation:** The scheduler processes unformatted records via Gemini API and sets `is_formatted = True`.
4. **Telegram Delivery:** Processed news is retrieved via CRUD queries and presented through inline keyboards (`single_slide()`).

---

## ⏰ Scheduler

The project uses APScheduler for automated background execution.
- Initialized in `app/bot/main.py`.
- Executes processing functions from `app/services/scheduler.py`.
- Configured with timezone: `Europe/Kiev`.

```text
Scheduler ──► run_parser() ──► Save new news ──► process_unformatted_news() ──► AI-formatted news
```

---

## 📄 Pagination & Navigation

### Database Pagination
Calculation formula: `offset = page * page_size`.
```text
Page 0 ──► OFFSET 0
Page 1 ──► OFFSET 5
Page 2 ──► OFFSET 10
```

### Regional Pagination
Regional news uses structured callback data containing `region` and `page`:
```text
User selects region ──► RegionNewsCallback ──► region = selected, page = 0 ──► Display article & build keyboard
```

---

## 🤖 Telegram Bot Interface

- `/start` — Initializes the user and opens the main menu.
- `/menu` — Returns the user to the main menu.
- **Latest News** — Displays the most recent AI-processed articles.
- **Regions** — Allows users to select a region and browse regional news.
- **Subscription** — Allows users to explicitly change their subscription status.

Example Interface:
```text
┌───────────────────────────────┐
│       📰 Latest News           │
├───────────────────────────────┤
│  ⬅️ Previous   1/10   ➡️ Next │
├───────────────────────────────┤
│          🔙 Back               │
└───────────────────────────────┘
```

---

## 🔐 Environment Configuration

Create a `.env` file in the project root:

```env
BOT_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key
```

- **`BOT_TOKEN`**: Telegram Bot API token obtained from [@BotFather](https://t.me/BotFather).
- **`GEMINI_API_KEY`**: Google Gemini API key obtained from Google AI Studio.

> ⚠️ **Security Notice:** Never commit `.env` or API credentials to the repository.

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/spirit-breaker228/BBC-Telegram-bot-.git
cd BBC-Telegram-bot-
```

### 2. Create and activate a virtual environment
- **Windows:**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
- **Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Copy `.env.example` to `.env` and fill in your credentials.

### 5. Run the application
Run the bot module directly:
```bash
python -m app.bot.main
```

The application initialization sequence:
```text
Initialize database ──► Create Bot ──► Register routers ──► Start scheduler ──► Start polling
```

---

## 🧪 Development Considerations

### Database Reliability
The current deduplication performs a `SELECT` check before `INSERT`. Concurrent execution may theoretically lead to race conditions. A production-ready enhancement includes:
- Stable article identifier or canonical URL.
- Database-level unique constraints.
- Atomic `UPSERT` statements and explicit `IntegrityError` handling.

### Query Efficiency & Performance
To eliminate N+1 query patterns and unnecessary DB round-trips:
- Batch queries & bulk inserts.
- Database-level upserts.

---

## 📈 Future Improvements

- [ ] Canonical URL or Source ID article identification.
- [ ] Safe concurrency deduplication mechanisms.
- [ ] Database migrations integration (Alembic).
- [ ] Automated unit and integration test suite.
- [ ] CI/CD automation pipelines.
- [ ] Advanced metrics, logging, and monitoring.

---

## 🧠 Engineering Concepts Demonstrated

- **Python & Async:** `asyncio`, asynchronous programming, modular architecture.
- **Telegram Bot Development:** `aiogram 3.x`, routers, handlers, inline keyboards, dynamic pagination, callback data.
- **Database Engineering:** SQLAlchemy 2.0 Async, ORM models, CRUD architecture, filtering, indexing, limit/offset pagination.
- **System Architecture:** Clean architecture, separation of concerns, scheduled background workflows, third-party API integration (Gemini AI, BBC RSS/HTML).

---

## 📊 Current Project Status

**Status:** Active Development

### Implemented Features:
- [x] Asynchronous BBC news parser
- [x] Database persistence & title deduplication
- [x] Gemini AI automated formatting & analysis
- [x] Interactive Telegram navigation & regional filtering
- [x] Background scheduler integration (APScheduler)
- [x] User management & subscription handling

---
