from datetime import datetime

from sqlalchemy import String, Integer, Float, ForeignKey, UniqueConstraint, Boolean
from sqlalchemy.orm import mapped_column, Mapped

from ..database import Base

class ItemModel(Base):
    __tablename__ = "item"
    __table_args__ = (UniqueConstraint("sticked_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=True)
    sticked_id: Mapped[str] = mapped_column(String, nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("product.id", onupdate='CASCADE', ondelete='SET NULL'), nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    is_in_stock: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_ready: Mapped[bool] = mapped_column(Boolean, nullable=False)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("order.id", onupdate='CASCADE', ondelete='SET NULL'), nullable=True)