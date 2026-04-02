import logging

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from asgiref.sync import sync_to_async
from jira import JIRA

from bot.keyboards import menu_keyboard, cancel_keyboard, CANCEL
from bot.states import PingStates

from core.services import ProfileService
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

router = Router()


async def _get_jira(user: User) -> JIRA:
    profile = await sync_to_async(lambda: user.profile)()
    url = f'https://{profile.company_name}.atlassian.net'
    return await sync_to_async(JIRA)(url, basic_auth=(profile.jira_login, profile.jira_token))


async def start_ping(message: Message, state: FSMContext, user: User) -> None:
    users = await sync_to_async(lambda: list(ProfileService.get_jira_users(user)))()
    if not users:
        await message.answer(
            'Sorry, there are no teammates in Jira Bot. '
            'Share @JiraAssistant_Bot with your team and ping them!',
            reply_markup=menu_keyboard(),
        )
        return

    # Build keyboard with display name (key)
    user_buttons: list[list[KeyboardButton]] = []
    user_map: dict[str, int] = {}
    for u in users:
        profile = await sync_to_async(lambda: u.profile)()
        label = f'{profile.jira_username_display} ({profile.jira_username_key})'
        user_buttons.append([KeyboardButton(text=label)])
        user_map[label] = u.id
    user_buttons.append([KeyboardButton(text=CANCEL)])

    kb = ReplyKeyboardMarkup(
        keyboard=user_buttons, resize_keyboard=True, one_time_keyboard=True,
    )
    await state.set_state(PingStates.select_user)
    await state.update_data(user_map=user_map)
    await message.answer('Select a user.', reply_markup=kb)


@router.message(PingStates.select_user, F.text == CANCEL)
async def ping_cancel_user(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer('Select an operation', reply_markup=menu_keyboard())


@router.message(PingStates.select_user)
async def ping_got_user(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    user_map = data.get('user_map', {})

    if message.text not in user_map:
        await message.answer('Please, choose an existing user.')
        return

    await state.update_data(
        selected_user_id=user_map[message.text],
        selected_user_label=message.text,
    )
    await state.set_state(PingStates.task_number)
    await message.answer('Enter task number to ping.')


@router.message(PingStates.task_number)
async def ping_got_task(message: Message, state: FSMContext, user: User) -> None:
    data = await state.get_data()
    selected_user_id = data['selected_user_id']
    selected_label = data['selected_user_label']

    jira = await _get_jira(user)
    profile = await sync_to_async(lambda: user.profile)()
    project = await sync_to_async(jira.project)(profile.project_id)
    task_number = f'{project.key}-{message.text}'

    url = f'https://{profile.company_name}.atlassian.net/browse/{task_number}'
    ping_msg = (
        f'User {profile.jira_username_display} pinged you about '
        f'task {task_number} - {url}'
    )

    # Get target user's chat_id
    target_user = await sync_to_async(User.objects.get)(id=selected_user_id)
    target_profile = await sync_to_async(lambda: target_user.profile)()

    try:
        bot: Bot = message.bot
        inline_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Open in browser', url=url)],
        ])
        await bot.send_message(
            chat_id=target_profile.chat_id,
            text=ping_msg,
            reply_markup=inline_kb,
        )
        result = f'Ping user {selected_label} for task {task_number} success!'
    except Exception as e:
        logger.error('Ping failed: %s', e)
        result = 'Ping Failure. Something went wrong, please try again.'

    await state.clear()
    await message.answer(result, reply_markup=menu_keyboard())
