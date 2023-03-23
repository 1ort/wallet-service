from datetime import datetime

from aiohttp.web import Request, Response, json_response


def create_user_handler(service):
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


def get_user_balance_handler(service):
    async def get_user_balance(request: Request) -> Response:
        user_id = request.match_info["user_id"]
        user = service.get_user(user_id)
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
            balance = service.calculate_balance(user, timestamp)
        else:
            balance = user.balance
        return json_response(
            {
                "user_id": user.id,
                "balance": balance,
            }
        )

    return get_user_balance


def get_user_handler(service):
    async def get_user(request: Request) -> Response:
        user_id = int(request.match_info["user_id"])
        user = service.get_user(user_id)
        if not user:
            return json_response(
                status=404,
                data={
                    "status": 404,
                    "error": "Not found",
                    "message": "User not found",
                },
            )
        return json_response(user.as_dict())

    return get_user


def add_transaction_handler(service):
    async def add_transaction(request: Request):
        return Response()

    return add_transaction


def get_transaction_handler(service):
    async def get_transaction(request: Request):
        return Response()

    return get_transaction


def add_routes(app, service, base_route: str = ""):
    app.router.add_route(
        "POST", rf"{base_route}/user", create_user_handler(service), name="create_user"
    )

    app.router.add_route(
        "GET",
        rf"{base_route}/user/{id}",
        get_user_handler(service),
        name="get_user",
    )
    app.router.add_route(
        "GET",
        rf"{base_route}/user/{id}/balance",
        get_user_balance_handler(service),
        name="get_user_balance",
    )
    app.router.add_route(
        "POST",
        rf"{base_route}/transaction",
        add_transaction_handler(service),
        name="add_transaction",
    )
    app.router.add_route(
        "GET",
        rf"{base_route}/transaction/{id}",
        get_transaction_handler(service),
        name="incoming_transaction",
    )
    ...
