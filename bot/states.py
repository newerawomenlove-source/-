from aiogram.fsm.state import State, StatesGroup


class SurveyStates(StatesGroup):
    waiting_custom_text = State()
