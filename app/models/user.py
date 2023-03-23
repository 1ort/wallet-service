from decimal import Decimal
from typing import List

from sqlalchemy import DECIMAL, CheckConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base, Transaction


class User(Base):
    __tablename__ = "user"
    __table_args__ = (CheckConstraint("balance>=0.00"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    balance: Mapped[Decimal] = mapped_column(DECIMAL(16, 2), default=0, nullable=False)
    transactions: Mapped[List[Transaction]] = relationship()
