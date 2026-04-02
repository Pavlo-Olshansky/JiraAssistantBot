import logging

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from asgiref.sync import sync_to_async
from jira import JIRA

from bot.keyboards import (
    menu_keyboard, VIEW_TASK, CREATE_TASK, PING_TASK, EDIT_TASK,
    AUTHORIZATION, FEEDBACK, SETTINGS,
)
from bot.states import (
    AuthStates, ViewTaskStates, CreateTaskStates, EditTaskStates,
    PingStates, FeedbackStates,
)

from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

router = Router()


async def _is_authorized(user: User) -> bool:
    """Check whether the user has saved Jira credentials that actually work."""
    profile = await sync_to_async(lambda: user.profile)()
    if not profile.jira_login or not profile.jira_token or not profile.company_name:
        return False
    try:
        url = f'https://{profile.company_name}.atlassian.net'
        jira = await sync_to_async(JIRA)(url, basic_auth=(profile.jira_login, profile.jira_token))
        users = await sync_to_async(jira.search_users)(profile.jira_login)
        if users:
            profile.jira_username_key = users[0].key
            profile.jira_username_display = users[0].displayName
            await sync_to_async(profile.save)()
            return True
    except Exception as e:
        logger.warning('Jira connection check failed: %s', e)
    return False


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, user: User) -> None:
    await state.clear()
    if await _is_authorized(user):
        await message.answer('Select an operation', reply_markup=menu_keyboard())
    else:
        await state.set_state(AuthStates.company_name)
        await message.answer(
            'Enter your Jira account name.\n(company from company.atlassian.net)'
        )


# ---- Main menu routing ----

@router.message(F.text == VIEW_TASK)
async def route_view_task(message: Message, state: FSMContext, user: User) -> None:
    from bot.handlers.tasks import ask_task_number_for_view
    await ask_task_number_for_view(message, state, user)


@router.message(F.text == CREATE_TASK)
async def route_create_task(message: Message, state: FSMContext, user: User) -> None:
    from bot.handlers.tasks import start_create_task
    await start_create_task(message, state, user)


@router.message(F.text == PING_TASK)
async def route_ping_task(message: Message, state: FSMContext, user: User) -> None:
    from bot.handlers.ping import start_ping
    await start_ping(message, state, user)


@router.message(F.text == EDIT_TASK)
async def route_edit_task(message: Message, state: FSMContext, user: User) -> None:
    from bot.handlers.tasks import ask_task_number_for_edit
    await ask_task_number_for_edit(message, state, user)


@router.message(F.text == AUTHORIZATION)
async def route_authorization(message: Message, state: FSMContext, user: User) -> None:
    from bot.handlers.auth import start_auth
    await start_auth(message, state, user)


@router.message(F.text == FEEDBACK)
async def route_feedback(message: Message, state: FSMContext) -> None:
    from bot.handlers.feedback import start_feedback
    await start_feedback(message, state)


@router.message(F.text == SETTINGS)
async def route_settings(message: Message, state: FSMContext, user: User) -> None:
    from bot.handlers.settings import start_settings
    await start_settings(message, state, user)
