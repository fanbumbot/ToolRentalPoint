from datetime import datetime, date
from typing import List

from sqlalchemy import Integer, String, ForeignKey, DateTime, Date, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship

from ..database import Base

from .product import ProductModel

class OrderModel(Base):
    __tablename__ = "order"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id", onupdate='CASCADE', ondelete='SET NULL'), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    registration_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint("registration_datetime", "user_id"),
    )

class OrderAndProductModel(Base):
    __tablename__ = "order_product"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("order.id", onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("product.id", onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    start_rent: Mapped[date] = mapped_column(Date, nullable=True)
    end_rent: Mapped[date] = mapped_column(Date, nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (UniqueConstraint("order_id", "product_id", "start_rent", "end_rent"),
        CheckConstraint("start_rent <= end_rent", name="check_order_product_start_end_rent"),
        CheckConstraint("quantity > 0", name="check_order_product_quantity")
    )