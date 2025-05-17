from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class ProductReviewView:
    id: int
    comment: str
    score: int
    publication_datetime: datetime
    user_name: str