from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database.engine import Base
from datetime import datetime  

class News(Base):
    __tablename__ = "news"
    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    summary: Mapped[str] = mapped_column(String)
    # Category
    location: Mapped[str] = mapped_column(String)

    # DateTime
    published_date: Mapped[datetime] = mapped_column(DateTime)
    formatted_title: Mapped[str | None] = mapped_column(String, nullable=True)

    # Formatted summary and analysis fields
    formatted_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    formatted_analysis: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Flag to indicate if the news has been formatted by AI
    is_published: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_formatted: Mapped[bool] = mapped_column(default=False, nullable=False)