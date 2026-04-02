from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Menu item constants (match base/menu.py)
VIEW_TASK = '\U0001f50d View task'
CREATE_TASK = '\U0001f4be Create task'
PING_TASK = '\U0001f4a1 Ping task'
EDIT_TASK = '\U0001f527 Edit task'
AUTHORIZATION = '\U0001f511 Authorization'
FEEDBACK = '\U0001f4e8 Feedback'
SETTINGS = '\u2699\ufe0f Settings'

YES = 'Yes'
NO = 'No'
CANCEL = '\u274c Cancel'
COMMENTS = '\U0001f4ac Comments'
TO_MENU = '\u2b05\ufe0f To menu'
ADD_COMMENT = '\U0001f195 Add comment'

TITLE = 'Title'
DESCRIPTION = 'Description'


def menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=VIEW_TASK), KeyboardButton(text=CREATE_TASK)],
            [KeyboardButton(text=PING_TASK), KeyboardButton(text=EDIT_TASK)],
            [KeyboardButton(text=AUTHORIZATION), KeyboardButton(text=FEEDBACK)],
            [KeyboardButton(text=SETTINGS)],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def yes_no_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=YES), KeyboardButton(text=NO)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=CANCEL)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def to_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=TO_MENU)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def task_action_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=EDIT_TASK), KeyboardButton(text=COMMENTS)],
            [KeyboardButton(text=TO_MENU)],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def comment_action_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=ADD_COMMENT), KeyboardButton(text=TO_MENU)],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def edit_field_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=TITLE), KeyboardButton(text=DESCRIPTION)],
            [KeyboardButton(text=CANCEL)],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
