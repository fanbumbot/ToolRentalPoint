from datetime import datetime

from sqlalchemy import String, Integer, Boolean, DateTime, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import mapped_column, Mapped

from ..database import Base

class DiscountPeriodModel(Base):
    __tablename__ = "discount_period"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=True)
    start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint("start", "end"),
        CheckConstraint("start < \"end\"", name="check_discount_period_start_end")
    )