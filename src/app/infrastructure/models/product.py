from sqlalchemy import String, Integer, Boolean, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.ext.hybrid import hybrid_property

from ..database import Base

class ProductModel(Base):
    __tablename__ = "product"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(32), nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("category.id", onupdate='CASCADE', ondelete='SET NULL'))
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    image: Mapped[str] = mapped_column(String(64), nullable=False)
    rent_or_buy_cost: Mapped[int] = mapped_column(Integer, nullable=False)
    standard_rental_period: Mapped[int] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_for_rent_or_sale: Mapped[bool] = mapped_column(Boolean, nullable=False)

    __table_args__ = (
        UniqueConstraint("slug"),
        CheckConstraint("rent_or_buy_cost >= 0", name="check_product_cost"),
        CheckConstraint("standard_rental_period > 0", name="check_product_period")
    )