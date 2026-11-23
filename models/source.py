from datetime import UTC, datetime

from pydantic import BaseModel, Field, HttpUrl


class SourceRecord(BaseModel):
    title: str = ""

    url: HttpUrl

    source_type: str = "unknown"

    excerpt: str = ""

    retrieved_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    search_score: float = 0.0
    source_score: float = 0.0