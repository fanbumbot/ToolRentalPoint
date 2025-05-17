from datetime import datetime

from sqlalchemy import String, Integer, Float, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import mapped_column, Mapped

from ..database import Base

class DiscountModel(Base):
    __tablename__ = "discount"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("product.id", onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    discount_period_id: Mapped[int] = mapped_column(Integer, ForeignKey("discount_period.id", onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    discount_value: Mapped[float] = mapped_column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint("product_id", "discount_period_id"),
        CheckConstraint("(discount_value >= 0.0) AND (discount_value <= 1.0)", name="check_discount")
    )