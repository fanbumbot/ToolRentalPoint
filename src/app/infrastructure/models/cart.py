from datetime import datetime, date
from typing import List

from sqlalchemy import Integer, String, ForeignKey, DateTime, Date, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship

from ..database import Base

from .product import ProductModel

class CartModel(Base):
    __tablename__ = "cart"
    __table_args__ = (UniqueConstraint("user_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id", onupdate='CASCADE', ondelete='CASCADE'), nullable=False)

class CartAndProductModel(Base):
    __tablename__ = "cart_product"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=True)
    cart_id: Mapped[int] = mapped_column(Integer, ForeignKey("cart.id", onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("product.id", onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    start_rent: Mapped[date] = mapped_column(Date, nullable=True)
    end_rent: Mapped[date] = mapped_column(Date, nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("cart_id", "product_id", "start_rent", "end_rent"),
        CheckConstraint("start_rent <= end_rent", name="check_cart_product_start_end_rent"),
        CheckConstraint("quantity > 0", name="check_cart_product_quantity")
    )