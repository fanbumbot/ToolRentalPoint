from datetime import datetime

from sqlalchemy import String, DateTime, Integer, Boolean, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import mapped_column, Mapped

from ..database import Base

class UserModel(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False,autoincrement=True)
    login: Mapped[str] = mapped_column(String(32), nullable=False)
    password: Mapped[str] = mapped_column(String(64), nullable=False)
    registration_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_login_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    blocked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    money: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint("login"),
        CheckConstraint(registration_datetime <= last_login_datetime, name="check_user_reg_log_datetime"),
        CheckConstraint("money >= 0", name="check_user_money")
    )