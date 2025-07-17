# Класс для состояний
from aiogram.fsm.state import StatesGroup, State
class MainMenuStates(StatesGroup):
    MAIN = State()
    WAIT_LOCATION = State()
    WAIT_PHOTO = State()