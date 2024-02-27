from aiogram.fsm.state import State, StatesGroup


class HRForm(StatesGroup):
    consent_question = State()
    get_name = State()
    restart = State()
    get_direction = State()
    get_year = State()
    get_sphere = State()
    get_sphere_details = State()
    internship_question = State()
    сover_letter = State()
    resume_question = State()
    get_resume = State()
    get_phone = State()
    full_time_question = State()
    finished = State()
