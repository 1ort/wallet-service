from aiohttp import web

from app.api import add_routes
from app.config import Config
from app.service import UserService, WalletService
from app.startups.database import get_database_session

config = Config()


def init_app() -> web.Application:
    app = web.Application()
    app["config"] = config
    app.on_startup.append(on_startup)
    return app


async def on_startup(app: web.Application):
    session = await get_database_session(config)
    # app["db_session"] = session
    user_service = UserService(session)

    wallet_service = WalletService(session)
    add_routes(app, user_service, wallet_service)
