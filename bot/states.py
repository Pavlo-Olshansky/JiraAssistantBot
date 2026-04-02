from aiogram.fsm.state import State, StatesGroup


class AuthStates(StatesGroup):
    company_name = State()
    login = State()
    token = State()


class ViewTaskStates(StatesGroup):
    task_number = State()
    viewing = State()


class CreateTaskStates(StatesGroup):
    title = State()
    description = State()


class EditTaskStates(StatesGroup):
    task_number = State()
    field_choice = State()
    new_value = State()


class PingStates(StatesGroup):
    select_user = State()
    task_number = State()


class SettingsStates(StatesGroup):
    choose_option = State()


class FeedbackStates(StatesGroup):
    enter_message = State()


class CommentStates(StatesGroup):
    enter_comment = State()
