from sqlalchemy import String, Integer, Boolean, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped

from ..database import Base

class CategoryModel(Base):
    __tablename__ = "category"
    __table_args__ = (UniqueConstraint("name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)