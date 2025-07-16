from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Suggestion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    input_text: str
    span_start: int
    span_end: int
    suggestion: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
