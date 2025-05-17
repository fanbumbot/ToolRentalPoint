from datetime import datetime

from sqlalchemy import String, Integer, DateTime, ForeignKey, UniqueConstraint, Boolean, CheckConstraint
from sqlalchemy.orm import mapped_column, Mapped

from ..database import Base

class ProductReviewModel(Base):
    __tablename__ = "product_review"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id", onupdate='CASCADE', ondelete='SET NULL'), nullable=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("product.id", onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str] = mapped_column(String, nullable=False)
    publication_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "product_id"),
        CheckConstraint("(score >= 0) AND (score <= 10)", name="check_product_review_score")
    )