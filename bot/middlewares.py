from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message
from asgiref.sync import sync_to_async

from core.services import ProfileService


class ProfileMiddleware(BaseMiddleware):
    """Attach the Django User (with profile) to every incoming message."""

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        tg_user = event.from_user
        user = await sync_to_async(ProfileService.get_or_create)(
            chat_id=str(event.chat.id),
            username=tg_user.username or str(tg_user.id),
            first_name=tg_user.first_name or '',
            last_name=tg_user.last_name or '',
        )
        data['user'] = user
        return await handler(event, data)
