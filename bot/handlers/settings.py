import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from asgiref.sync import sync_to_async

from bot.keyboards import menu_keyboard, TO_MENU
from bot.states import SettingsStates

from core.services import ProfileService
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

router = Router()

# All notification boolean fields on Profile
NOTIFY_FIELDS = [
    'notify_only_my_assignee',
    'notify_on_task_created',
    'notify_on_task_updeted',
    'notify_on_task_deleted',
    'notify_on_attachment_created',
    'notify_on_attachment_deleted',
    'notify_on_comment_created',
    'notify_on_comment_updeted',
    'notify_on_comment_deleted',
    'notify_on_version_created',
    'notify_on_version_updeted',
    'notify_on_version_deleted',
    'notify_on_version_released',
    'notify_on_sprint_created',
    'notify_on_sprint_updeted',
    'notify_on_sprint_deleted',
    'notify_on_sprint_started',
    'notify_on_sprint_closed',
]


def _human_label(field: str) -> str:
    """Convert field name to a readable label."""
    return field.replace('_', ' ').replace('notify ', '').capitalize()


def _settings_keyboard(profile) -> ReplyKeyboardMarkup:
    """Build a keyboard showing each setting with its current on/off state."""
    buttons: list[list[KeyboardButton]] = []
    for field in NOTIFY_FIELDS:
        value = getattr(profile, field)
        icon = '\u2705' if value else '\u274c'
        label = f'{icon} {_human_label(field)}'
        buttons.append([KeyboardButton(text=label)])
    buttons.append([KeyboardButton(text=TO_MENU)])
    return ReplyKeyboardMarkup(
        keyboard=buttons, resize_keyboard=True, one_time_keyboard=True,
    )


async def start_settings(message: Message, state: FSMContext, user: User) -> None:
    profile = await sync_to_async(lambda: user.profile)()
    await state.set_state(SettingsStates.choose_option)
    await message.answer(
        'Notification settings (tap to toggle):',
        reply_markup=_settings_keyboard(profile),
    )


@router.message(SettingsStates.choose_option, F.text == TO_MENU)
async def settings_to_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer('Select an operation', reply_markup=menu_keyboard())


@router.message(SettingsStates.choose_option)
async def toggle_setting(message: Message, state: FSMContext, user: User) -> None:
    text = message.text or ''
    # Strip the leading icon
    stripped = text.lstrip('\u2705\u274c').strip()

    # Match against known labels
    target_field = None
    for field in NOTIFY_FIELDS:
        if _human_label(field) == stripped:
            target_field = field
            break

    if not target_field:
        await message.answer('Please choose a valid option.')
        return

    profile = await sync_to_async(lambda: user.profile)()
    current = getattr(profile, target_field)
    new_value = not current
    await sync_to_async(ProfileService.update_setting)(user, target_field, new_value)

    # Refresh profile and show updated keyboard
    profile = await sync_to_async(ProfileService.get_profile)(user)
    status = 'ON' if new_value else 'OFF'
    await message.answer(
        f'{_human_label(target_field)}: {status}',
        reply_markup=_settings_keyboard(profile),
    )
