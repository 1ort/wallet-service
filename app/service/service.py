from datetime import datetime
from decimal import Decimal

from app.models import User


class WalletService:
    async def create_user(self, username: str) -> User:
        new_user = User(name=username)
        ...
        return new_user

    async def get_user(self, user_id: int) -> User | None:
        return User()

    async def withdraw(
        self,
    ) -> None:
        pass

    async def deposit(
        self,
    ) -> None:
        pass

    async def get_balance(self, user: User, at_time: datetime | None = None) -> Decimal:
        return Decimal(0.0)

    async def _calculate_balance(self, user: User, at_time: datetime) -> Decimal:
        return Decimal(0.0)
