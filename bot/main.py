import asyncio
import logging
import os
import sys

import django


def _setup_django() -> None:
    """Bootstrap Django before importing any models."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_microservice.settings')
    # Ensure project root is on sys.path so `core`, `django_microservice` etc. resolve
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    django.setup()


_setup_django()

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from django.conf import settings as django_settings

from bot.middlewares import ProfileMiddleware
from bot.handlers import start, auth, tasks, comments, ping, settings, feedback

logger = logging.getLogger(__name__)


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())

    # Register profile middleware on all message handlers
    dp.message.middleware(ProfileMiddleware())

    # Include routers (order matters: start router is a catch-all for menu texts)
    dp.include_router(auth.router)
    dp.include_router(tasks.router)
    dp.include_router(comments.router)
    dp.include_router(ping.router)
    dp.include_router(settings.router)
    dp.include_router(feedback.router)
    dp.include_router(start.router)  # last — contains menu text filters

    return dp


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    )

    bot = Bot(token=django_settings.TELEGRAM_API_KEY)
    dp = create_dispatcher()

    logger.info('Starting bot polling...')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
