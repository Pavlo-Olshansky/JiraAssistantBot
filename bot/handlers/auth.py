import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from asgiref.sync import sync_to_async
from jira import JIRA

from bot.keyboards import menu_keyboard, yes_no_keyboard, YES, CANCEL
from bot.states import AuthStates

from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

router = Router()

TOKEN_URL = 'https://id.atlassian.com/manage/api-tokens'


async def start_auth(message: Message, state: FSMContext, user: User) -> None:
    """Show current credentials and offer to re-authorize."""
    profile = await sync_to_async(lambda: user.profile)()
    try:
        jira = await sync_to_async(JIRA)(
            f'https://{profile.company_name}.atlassian.net',
            basic_auth=(profile.jira_login, profile.jira_token),
        )
        project = await sync_to_async(jira.project)(profile.project_id)
        project_name = project.name
    except Exception:
        project_name = 'N/A'

    msg = (
        f'Current credentials:\n'
        f'Company: `{profile.company_name}`\n'
        f'Login: `{profile.jira_login}`\n'
        f'Token: `{profile.jira_token}`\n'
        f'Project: `{project_name}`\n\n'
        f'Do you want to change your credentials?'
    )
    await state.set_state(AuthStates.company_name)
    await state.update_data(confirm_change=True)
    await message.answer(msg, parse_mode='Markdown', reply_markup=yes_no_keyboard())


@router.message(AuthStates.company_name)
async def on_company_name(message: Message, state: FSMContext) -> None:
    data = await state.get_data()

    # If we asked for confirmation first, handle Yes/No
    if data.get('confirm_change'):
        await state.update_data(confirm_change=False)
        if message.text != YES:
            await state.clear()
            await message.answer('Select an operation', reply_markup=menu_keyboard())
            return
        await message.answer(
            'Enter your Jira account name.\n(company from company.atlassian.net)'
        )
        return

    await state.update_data(company_name=message.text)
    await state.set_state(AuthStates.login)
    await message.answer('Enter your Jira account login or email')


@router.message(AuthStates.login)
async def on_login(message: Message, state: FSMContext) -> None:
    await state.update_data(login=message.text)
    await state.set_state(AuthStates.token)
    await message.answer(
        f'Enter your token.\nYou can create your token here - {TOKEN_URL}'
    )


@router.message(AuthStates.token)
async def on_token(message: Message, state: FSMContext, user: User) -> None:
    data = await state.get_data()
    company = data['company_name']
    login = data['login']
    token = message.text

    profile = await sync_to_async(lambda: user.profile)()
    profile.company_name = company
    profile.jira_login = login
    profile.jira_token = token

    # Validate connection
    try:
        url = f'https://{company}.atlassian.net'
        jira = await sync_to_async(JIRA)(url, basic_auth=(login, token))
        users = await sync_to_async(jira.search_users)(login)
        if users:
            profile.jira_username_key = users[0].key
            profile.jira_username_display = users[0].displayName
    except Exception as e:
        logger.warning('Jira auth failed: %s', e)
        await state.clear()
        await message.answer(
            'Sorry, you are not authorized!\n'
            'Try login again by typing /start.'
        )
        return

    # Pick project
    try:
        projects = await sync_to_async(jira.projects)()
    except Exception:
        projects = []

    if not projects:
        browse_url = (
            f'https://{company}.atlassian.net/secure/BrowseProjects.jspa'
            f'?page=1&selectedCategory=all&selectedProjectType=all'
            f'&sortKey=name&sortOrder=ASC'
        )
        await state.clear()
        await message.answer(
            f'Sorry, you have no project yet. '
            f'Please, create a new one and authorize again.\n{browse_url}'
        )
        return

    if len(projects) == 1:
        project = projects[0]
    else:
        # Store projects in state, ask user to pick
        project_names = [p.name for p in projects]
        await state.update_data(
            projects={p.name: p.id for p in projects},
            awaiting_project=True,
        )
        from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
        kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=name)] for name in project_names],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        await message.answer('Choose your project:', reply_markup=kb)
        # Stay in token state to handle project selection
        return

    profile.project_id = project.id
    await sync_to_async(profile.save)()

    display = profile.jira_username_display
    name_part = f', {display}' if display else ''
    await state.clear()
    await message.answer(
        f'Welcome{name_part}! You are logged in successfully.',
        reply_markup=menu_keyboard(),
    )
