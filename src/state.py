from dataclasses import dataclass, field
from typing import List, Optional, TypedDict, Annotated
import operator

@dataclass
class Article:
    source: str  # 'arxiv', 'rss', etc.
    title: str
    url: str
    content: str  # Abstract or summary
    author: Optional[str] = None
    date: Optional[str] = None
    category: Optional[str] = None
    relevance_score: float = 0.0
    summary: Optional[str] = None
    insight: Optional[str] = None
    raw_data: dict = field(default_factory=dict)

class AgentState(TypedDict):
    articles: List[Article]
    # We can add logs or status flags here if needed
