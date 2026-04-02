import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from asgiref.sync import sync_to_async
from jira import JIRA

from bot.keyboards import (
    menu_keyboard, yes_no_keyboard, cancel_keyboard, task_action_keyboard,
    edit_field_keyboard, to_menu_keyboard,
    YES, CANCEL, EDIT_TASK, COMMENTS, TO_MENU, TITLE, DESCRIPTION,
)
from bot.states import ViewTaskStates, CreateTaskStates, EditTaskStates

from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

router = Router()


# ---- Helpers ----

async def _get_jira(user: User) -> JIRA:
    profile = await sync_to_async(lambda: user.profile)()
    url = f'https://{profile.company_name}.atlassian.net'
    return await sync_to_async(JIRA)(url, basic_auth=(profile.jira_login, profile.jira_token))


async def _get_project_key(user: User) -> str:
    jira = await _get_jira(user)
    profile = await sync_to_async(lambda: user.profile)()
    project = await sync_to_async(jira.project)(profile.project_id)
    return project.key


async def _task_url(user: User, task_number: str) -> str:
    profile = await sync_to_async(lambda: user.profile)()
    return f'https://{profile.company_name}.atlassian.net/browse/{task_number}'


# ===========================================================
#  VIEW TASK
# ===========================================================

async def ask_task_number_for_view(message: Message, state: FSMContext, user: User) -> None:
    project_key = await _get_project_key(user)
    await state.set_state(ViewTaskStates.task_number)
    await state.update_data(project_key=project_key)
    await message.answer(f'Enter task number:\n`{project_key}-`', parse_mode='Markdown')


@router.message(ViewTaskStates.task_number)
async def view_task_got_number(message: Message, state: FSMContext, user: User) -> None:
    data = await state.get_data()
    project_key = data['project_key']
    task_number = f'{project_key}-{message.text}'

    try:
        jira = await _get_jira(user)
        issue = await sync_to_async(jira.issue)(task_number)
    except Exception as e:
        logger.warning('Task lookup failed: %s', e)
        await state.clear()
        await message.answer(
            f'Sorry, task {task_number} does not exist.',
            reply_markup=menu_keyboard(),
        )
        return

    labels = ' '.join(issue.fields.labels) if issue.fields.labels else ''
    labels_line = f'\nLabels: `{labels}`' if labels else ''
    url = await _task_url(user, task_number)
    text = (
        f'`{issue.fields.summary}`{labels_line}\n\n'
        f'{issue.fields.description}\n\n{url}'
    )

    await state.set_state(ViewTaskStates.viewing)
    await state.update_data(task_key=issue.key)
    await message.answer(text, parse_mode='Markdown', reply_markup=task_action_keyboard())


@router.message(ViewTaskStates.viewing, F.text == EDIT_TASK)
async def view_then_edit(message: Message, state: FSMContext, user: User) -> None:
    data = await state.get_data()
    task_key = data['task_key']
    jira = await _get_jira(user)
    try:
        issue = await sync_to_async(jira.issue)(task_key)
    except Exception:
        await state.clear()
        await message.answer('Could not load the task.', reply_markup=menu_keyboard())
        return

    msg = f'Edit task {issue.key} ? (`{issue.fields.summary}`)'
    await state.set_state(EditTaskStates.field_choice)
    await state.update_data(task_key=issue.key)
    await message.answer(msg, parse_mode='Markdown', reply_markup=yes_no_keyboard())


@router.message(ViewTaskStates.viewing, F.text == COMMENTS)
async def view_then_comments(message: Message, state: FSMContext, user: User) -> None:
    from bot.handlers.comments import show_comments
    data = await state.get_data()
    await show_comments(message, state, user, data['task_key'])


@router.message(ViewTaskStates.viewing, F.text == TO_MENU)
async def view_to_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer('Select an operation', reply_markup=menu_keyboard())


# ===========================================================
#  CREATE TASK
# ===========================================================

async def start_create_task(message: Message, state: FSMContext, user: User) -> None:
    jira = await _get_jira(user)
    profile = await sync_to_async(lambda: user.profile)()
    project = await sync_to_async(jira.project)(profile.project_id)
    await state.update_data(project_id=project.id, project_name=project.name)
    await state.set_state(CreateTaskStates.title)
    await message.answer(
        f'Create new task for project `{project.name}` ?\n'
        f'Enter task *title* (or {CANCEL} to abort):',
        parse_mode='Markdown',
        reply_markup=cancel_keyboard(),
    )


@router.message(CreateTaskStates.title, F.text == CANCEL)
async def create_cancel_title(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer('Select an operation', reply_markup=menu_keyboard())


@router.message(CreateTaskStates.title)
async def create_got_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await state.set_state(CreateTaskStates.description)
    await message.answer(
        'Enter task <b>description</b>:',
        parse_mode='HTML',
        reply_markup=cancel_keyboard(),
    )


@router.message(CreateTaskStates.description, F.text == CANCEL)
async def create_cancel_desc(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer('Select an operation', reply_markup=menu_keyboard())


@router.message(CreateTaskStates.description)
async def create_got_description(message: Message, state: FSMContext, user: User) -> None:
    data = await state.get_data()
    jira = await _get_jira(user)
    try:
        new_issue = await sync_to_async(jira.create_issue)(
            project={'id': data['project_id']},
            summary=data['title'],
            description=message.text,
            issuetype={'name': 'Story'},
        )
    except Exception as e:
        logger.error('Create task failed: %s', e)
        await state.clear()
        await message.answer('Error. Task is not created.', reply_markup=menu_keyboard())
        return

    url = await _task_url(user, new_issue.key)
    await state.clear()
    await message.answer(
        f'Task {new_issue.key} created.\n{url}',
        reply_markup=menu_keyboard(),
    )


# ===========================================================
#  EDIT TASK
# ===========================================================

async def ask_task_number_for_edit(message: Message, state: FSMContext, user: User) -> None:
    project_key = await _get_project_key(user)
    await state.set_state(EditTaskStates.task_number)
    await state.update_data(project_key=project_key)
    await message.answer(f'Enter task number:\n`{project_key}-`', parse_mode='Markdown')


@router.message(EditTaskStates.task_number)
async def edit_got_number(message: Message, state: FSMContext, user: User) -> None:
    data = await state.get_data()
    project_key = data['project_key']
    task_number = f'{project_key}-{message.text}'

    jira = await _get_jira(user)
    try:
        issue = await sync_to_async(jira.issue)(task_number)
    except Exception as e:
        logger.warning('Edit task lookup failed: %s', e)
        await state.clear()
        await message.answer(
            f'Sorry, task {task_number} does not exist.',
            reply_markup=menu_keyboard(),
        )
        return

    msg = f'Edit task {issue.key} ? (`{issue.fields.summary}`)'
    await state.set_state(EditTaskStates.field_choice)
    await state.update_data(task_key=issue.key)
    await message.answer(msg, parse_mode='Markdown', reply_markup=yes_no_keyboard())


@router.message(EditTaskStates.field_choice)
async def edit_field_choice(message: Message, state: FSMContext) -> None:
    if message.text == YES:
        await message.answer('What do you want to edit?', reply_markup=edit_field_keyboard())
        return

    if message.text in (TITLE, DESCRIPTION):
        data = await state.get_data()
        await state.update_data(edit_field=message.text)
        await state.set_state(EditTaskStates.new_value)
        if message.text == TITLE:
            await message.answer(
                f'Enter new title for task {data["task_key"]}:',
                reply_markup=cancel_keyboard(),
            )
        else:
            await message.answer(
                f'Enter new description for task {data["task_key"]}:',
                reply_markup=cancel_keyboard(),
            )
        return

    if message.text == CANCEL:
        await state.clear()
        await message.answer('Select an operation', reply_markup=menu_keyboard())
        return

    # "No" or invalid
    await state.clear()
    await message.answer('Select an operation', reply_markup=menu_keyboard())


@router.message(EditTaskStates.new_value, F.text == CANCEL)
async def edit_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer('Select an operation', reply_markup=menu_keyboard())


@router.message(EditTaskStates.new_value)
async def edit_got_value(message: Message, state: FSMContext, user: User) -> None:
    data = await state.get_data()
    task_key = data['task_key']
    field = data['edit_field']

    jira = await _get_jira(user)
    try:
        issue = await sync_to_async(jira.issue)(task_key)
        if field == TITLE:
            await sync_to_async(issue.update)(summary=message.text)
            result = f'Title for task {task_key} updated!'
        else:
            await sync_to_async(issue.update)(description=message.text)
            result = f'Description for task {task_key} updated!'
    except Exception as e:
        logger.error('Edit task failed: %s', e)
        field_name = 'Title' if field == TITLE else 'Description'
        result = f'Error. {field_name} for task {task_key} is not updated.'

    await state.clear()
    await message.answer(result, reply_markup=menu_keyboard())
