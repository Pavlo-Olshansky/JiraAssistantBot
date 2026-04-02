import logging

from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from django.conf import settings as django_settings

from bot.keyboards import menu_keyboard, cancel_keyboard, CANCEL
from bot.states import FeedbackStates

logger = logging.getLogger(__name__)

router = Router()


async def start_feedback(message: Message, state: FSMContext) -> None:
    await state.set_state(FeedbackStates.enter_message)
    await message.answer('Please, write a feedback:', reply_markup=cancel_keyboard())


@router.message(FeedbackStates.enter_message)
async def got_feedback(message: Message, state: FSMContext) -> None:
    if message.text == CANCEL:
        await state.clear()
        await message.answer('Select an operation', reply_markup=menu_keyboard())
        return

    chat_id = django_settings.FEEDBACK_RECEIVER_CHAT_ID
    if chat_id:
        try:
            bot: Bot = message.bot
            await bot.send_message(
                chat_id=chat_id,
                text=f'Feedback received:\n{message.text}',
            )
            await state.clear()
            await message.answer(
                'Thanks! We will consider your wishes.',
                reply_markup=menu_keyboard(),
            )
            return
        except Exception as e:
            logger.error('Failed to send feedback: %s', e)

    await state.clear()
    await message.answer('Sorry, an error occurred.', reply_markup=menu_keyboard())
