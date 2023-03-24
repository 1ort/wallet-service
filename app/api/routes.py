from datetime import datetime
from decimal import Decimal
from typing import cast
from uuid import UUID

from aiohttp.web import Request, Response, json_response

from app.models import Transaction, TransactionType, User
from app.service import InsufficientFunds, UserService, WalletService


async def get_current_user(request: Request, user_service: UserService) -> User | None:
    user_id = request.match_info["user_id"]
    return await get_user_from_id_str(user_id, user_service)


async def get_user_from_id_str(
    user_id_str: str, user_service: UserService
) -> User | None:
    try:
        user_id = int(user_id_str)
    except ValueError:
        return None
    user = await user_service.get_user(user_id)
    return user


def create_user_handler(service: UserService):
    async def create_user(request) -> Response:
        user_data = await request.json()
        username = user_data.get("name")
        if not username:
            return json_response(
                status=400,
                data={
                    "status": 400,
                    "error": "Bad Request",
                    "message": 'Provide "name".',
                },
            )

        new_user = await service.create_user(username)
        return json_response(new_user.as_dict())

    return create_user


def get_user_balance_handler(user_service: UserService, wallet_service: WalletService):
    async def get_user_balance(request: Request) -> Response:
        user = await get_current_user(request, user_service)
        if not user:
            return json_response(
                status=404,
                data={
                    "status": 404,
                    "error": "Not found",
                    "message": "User not found",
                },
            )
        timestamp_str = request.query.get("timestamp")
        if timestamp_str:
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
            except ValueError:
                return json_response(
                    status=400,
                    data={
                        "status": 400,
                        "error": "Bad Request",
                        "message": "Invalid timestamp format",
                    },
                )
            balance = wallet_service.calculate_balance(user, timestamp)
        else:
            balance = user.balance
        return json_response(
            {
                "user_id": user.id,
                "balance": balance,
            }
        )

    return get_user_balance


def get_user_handler(user_service: UserService):
    async def get_user(request: Request) -> Response:
        user = await get_current_user(request, user_service)
        if not user:
            return json_response(
                status=404,
                data={
                    "status": 404,
                    "error": "Not found",
                    "message": f"User not found",
                },
            )
        return json_response(user.as_dict())

    return get_user


def parse_transaction(d: dict[str, str]) -> Transaction | None:
    uid = d.get("uid")
    amount = d.get("amount")
    tr_type = d.get("type")
    timestamp = d.get("timestamp")
    user_id = d.get("user_id")

    if not all([uid, amount, tr_type, timestamp, user_id]):
        return None
    try:
        uid = UUID(uid)
        amount = Decimal(cast(str, user_id))
        tr_type = TransactionType["tr_type"]
        timestamp = datetime.fromisoformat(cast(str, timestamp))
        user_id = int(cast(str, timestamp))
    except:  # TODO: каждая конвертация может кидать разные исключения
        return None
    return Transaction(
        uid=uid, amount=amount, user_id=user_id, timestamp=timestamp, type=tr_type
    )


def add_transaction_handler(user_service: UserService, wallet_service: WalletService):
    async def add_transaction(request: Request):
        req_json = await request.json()
        transaction = parse_transaction(req_json)
        if not transaction:
            return json_response(
                status=400,
                data={
                    "status": 404,
                    "error": "Bad request",
                    "message": "Bad transaction format",
                },
            )
        user = await user_service.get_user(transaction.user_id)
        if not user:
            return json_response(
                status=404,
                data={
                    "status": 404,
                    "error": "Not found",
                    "message": "User not found",
                },
            )
        try:
            await wallet_service.execute_transaction(user, transaction)
        except InsufficientFunds:
            return json_response(
                status=402,
                data={
                    "status": 402,
                    "error": "Insufficient funds",
                    "message": "Insufficient funds",
                },
            )
        return Response()

    return add_transaction


def get_transaction_handler(service: WalletService):
    async def get_transaction(request: Request) -> Response:
        transaction_id = UUID(hex=request.match_info["id"])
        transaction = await service.get_transaction(transaction_id)
        if not transaction:
            return json_response(
                status=404,
                data={
                    "status": 404,
                    "error": "Not found",
                    "message": "Transaction not found",
                },
            )
        return json_response(transaction.as_dict())

    return get_transaction


def add_routes(
    app, user_service: UserService, wallet_service: WalletService, base_route: str = ""
):
    app.router.add_route(
        "POST",
        rf"{base_route}/user",
        create_user_handler(user_service),
        name="create_user",
    )

    app.router.add_route(
        "GET",
        rf"{base_route}/user/{id}",
        get_user_handler(user_service),
        name="get_user",
    )
    app.router.add_route(
        "GET",
        rf"{base_route}/user/{id}/balance",
        get_user_balance_handler(user_service, wallet_service),
        name="get_user_balance",
    )
    app.router.add_route(
        "POST",
        rf"{base_route}/transaction",
        add_transaction_handler(user_service, wallet_service),
        name="add_transaction",
    )
    app.router.add_route(
        "GET",
        rf"{base_route}/transaction/{id}",
        get_transaction_handler(wallet_service),
        name="incoming_transaction",
    )
    ...
