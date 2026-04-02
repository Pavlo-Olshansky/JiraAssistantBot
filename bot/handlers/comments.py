import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from asgiref.sync import sync_to_async
from jira import JIRA

from bot.keyboards import (
    menu_keyboard, comment_action_keyboard, to_menu_keyboard,
    ADD_COMMENT, TO_MENU,
)
from bot.states import CommentStates

from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

router = Router()


async def _get_jira(user: User) -> JIRA:
    profile = await sync_to_async(lambda: user.profile)()
    url = f'https://{profile.company_name}.atlassian.net'
    return await sync_to_async(JIRA)(url, basic_auth=(profile.jira_login, profile.jira_token))


async def show_comments(message: Message, state: FSMContext, user: User, task_key: str) -> None:
    """Display comments for a task and offer Add comment / To menu."""
    jira = await _get_jira(user)
    try:
        issue = await sync_to_async(jira.issue)(task_key)
        comments = await sync_to_async(jira.comments)(issue)
    except Exception as e:
        logger.warning('Failed to fetch comments: %s', e)
        await state.clear()
        await message.answer('Could not load comments.', reply_markup=menu_keyboard())
        return

    if comments:
        lines = [f'`{c.author}`: {c.body}' for c in comments]
        text = '\n'.join(lines)
        await message.answer(text, parse_mode='Markdown', reply_markup=comment_action_keyboard())
    else:
        await message.answer(
            f'There are no comments on task {task_key}',
            reply_markup=comment_action_keyboard(),
        )

    await state.set_state(CommentStates.enter_comment)
    await state.update_data(task_key=task_key, awaiting_action=True)


@router.message(CommentStates.enter_comment, F.text == ADD_COMMENT)
async def prompt_new_comment(message: Message, state: FSMContext) -> None:
    await state.update_data(awaiting_action=False)
    await message.answer('Please, enter new comment:')


@router.message(CommentStates.enter_comment, F.text == TO_MENU)
async def comments_to_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer('Select an operation', reply_markup=menu_keyboard())


@router.message(CommentStates.enter_comment)
async def add_comment(message: Message, state: FSMContext, user: User) -> None:
    data = await state.get_data()

    # If user hasn't pressed "Add comment" yet, treat as going back
    if data.get('awaiting_action'):
        await state.clear()
        await message.answer('Select an operation', reply_markup=menu_keyboard())
        return

    task_key = data['task_key']
    jira = await _get_jira(user)
    try:
        await sync_to_async(jira.add_comment)(task_key, message.text)
        result = f'Comment for task {task_key} created.'
    except Exception as e:
        logger.error('Add comment failed: %s', e)
        result = f'Error adding comment to {task_key}.'

    await state.clear()
    await message.answer(result, reply_markup=menu_keyboard())
