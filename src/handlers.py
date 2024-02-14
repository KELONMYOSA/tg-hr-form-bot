from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from src.keyboard import make_row_keyboard
from src.states import HRForm
from src.utils import send_results_email, sphere_dict

router = Router()


# Старт бота, спрашиваем про обработку персональных данных
@router.message(StateFilter(None), Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Привет! Спасибо за проявленный интерес к работе в Комфортел!\n"
        "Чтобы мы могли договориться о дальнейшем сотрудничестве, "
        "нам важно получить от тебя некоторую информацию.\n\n"
        "Ты даёшь согласие на обработку своих данных?",
        reply_markup=make_row_keyboard(["Да", "Нет"]),
    )
    await state.set_state(HRForm.consent_question)


# Согласие или нет на обработку
@router.message(HRForm.consent_question, F.text.in_(["Да", "Нет"]))
async def consent_question(message: Message, state: FSMContext):
    if message.text == "Да":
        await message.answer(
            text="Отлично! Давай знакомиться.\n"
            "Я чат-бот компании Комфортел.\n"
            "Напиши, пожалуйста, как тебя зовут? (формат: Фамилия Имя)",
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.set_state(HRForm.get_name)
    else:
        await message.answer(
            text="Нам очень жаль!\n"
            "Твои контакты нужны исключительно для HR-менеджера. В ближайшее время он свяжется с тобой, "
            "чтобы обсудить возможные варианты сотрудничества.\n\n"
            "Начнем заново?",
            reply_markup=make_row_keyboard(["Начать сначала"]),
        )
        await state.set_state(HRForm.restart)


# Отказ в обработке данных
@router.message(HRForm.restart, F.text.in_(["Начать сначала"]))
async def restart(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Привет! Спасибо за проявленный интерес к работе в Комфортел!\n"
        "Чтобы мы могли договориться о дальнейшем сотрудничестве, "
        "нам важно получить от тебя некоторую информацию.\n\n"
        "Ты даёшь согласие на обработку своих данных?",
        reply_markup=make_row_keyboard(["Да", "Нет"]),
    )
    await state.set_state(HRForm.consent_question)


# Получаем имя и спрашиваем направление
@router.message(HRForm.get_name)
async def direction_question(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(text="На каком направлении ты учишься?", reply_markup=ReplyKeyboardRemove())
    await state.set_state(HRForm.get_direction)


# Получаем направление и спрашиваем курс
@router.message(HRForm.get_direction)
async def year_question(message: Message, state: FSMContext):
    await state.update_data(direction=message.text)
    await message.answer(text="А курс?", reply_markup=ReplyKeyboardRemove())
    await state.set_state(HRForm.get_year)


# Получаем курс и спрашиваем о сферах деятельности
@router.message(HRForm.get_year)
async def sphere_question(message: Message, state: FSMContext):
    await state.update_data(year=message.text)
    await message.answer(
        text="Мы всегда рады предложить интересные карьерные возможности.\n"
        "Пожалуйста, выбери сферу, в которой бы тебе хотелось развиваться (указать цифру):\n"
        "1. Разработка\n"
        "2. Техническая поддержка\n"
        "3. Инфраструктура, сети\n"
        "4. Управление проектами (телеком, IT)\n"
        "5. B2B Продажи\n"
        "6. Финансы, бухгалтерия\n"
        "7. HR, психология\n"
        "8. PR, маркетинг, event, графический дизайн\n"
        "9. Другое",
        reply_markup=make_row_keyboard([str(x) for x in range(1, 10)]),
    )
    await state.set_state(HRForm.get_sphere)


# Если ответ 9, спрашиваем подробнее
@router.message(HRForm.get_sphere, F.text.in_(["9"]))
async def other_sphere_question(message: Message, state: FSMContext):
    await message.answer(
        text="Опиши свои пожелания к будущему месту работы (условия, график, команда, задачи и др.)",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(HRForm.get_sphere_details)


# Если сфера 1-8, спрашиваем про стажировку
@router.message(HRForm.get_sphere, F.text.in_([str(x) for x in range(1, 9)]))
async def internship_question_1(message: Message, state: FSMContext):
    await state.update_data(sphere=sphere_dict[message.text])
    await message.answer(text="Ты заинтересован в стажировке/практике?", reply_markup=make_row_keyboard(["Да", "Нет"]))
    await state.set_state(HRForm.internship_question)


# Получаем подробности о сфере и спрашиваем про стажировку
@router.message(HRForm.get_sphere_details)
async def internship_question_2(message: Message, state: FSMContext):
    await state.update_data(sphere=f"Другое. {message.text}")
    await message.answer(text="Ты заинтересован в стажировке/практике?", reply_markup=make_row_keyboard(["Да", "Нет"]))
    await state.set_state(HRForm.internship_question)


# Получение ответа на вопрос о стажировке
@router.message(HRForm.internship_question, F.text.in_(["Да", "Нет"]))
async def internship_answer(message: Message, state: FSMContext):
    if message.text == "Да":
        await state.update_data(intern="Да")
        await state.update_data(full_time="Нет")
        await message.answer(
            text="Да это мэтч!\n"
            "Не стесняйся, пиши рекрутеру компании Анне Кучер в tg - @kucher_hr, "
            "указав примерные даты практики/стажировки и три вещи, которым хочешь научиться у нас."
        )
        await message.answer(
            text="А теперь финальный этап!\n" "Напиши свой контактный телефон в формате +7 ХХХ ХХХ-ХХ-ХХ",
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.set_state(HRForm.get_phone)
    else:
        await state.update_data(intern="Нет")
        await message.answer(
            text="Ты заинтересован в работе на полный день?", reply_markup=make_row_keyboard(["Да", "Нет", "Назад"])
        )
        await state.set_state(HRForm.full_time_question)


# Получение ответа на вопрос о полном рабочем дне
@router.message(HRForm.full_time_question, F.text.in_(["Да", "Нет", "Назад"]))
async def full_time_answer(message: Message, state: FSMContext):
    if message.text == "Да":
        await state.update_data(full_time="Да")
        await message.answer(
            text="Смело отправляй свое резюме и сопроводительное письмо на почту hh@comfortel.pro, "
            "указав почему ты хочешь работать именно у нас."
        )
        await message.answer(
            text="А теперь финальный этап!\n" "Напиши свой контактный телефон в формате +7 ХХХ ХХХ-ХХ-ХХ",
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.set_state(HRForm.get_phone)
    elif message.text == "Нет":
        await state.update_data(full_time="Нет")
        await message.answer(
            text="А теперь финальный этап!\n" "Напиши свой контактный телефон в формате +7 ХХХ ХХХ-ХХ-ХХ",
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.set_state(HRForm.get_phone)
    else:
        await message.answer(
            text="Ты заинтересован в стажировке/практике?", reply_markup=make_row_keyboard(["Да", "Нет"])
        )
        await state.set_state(HRForm.internship_question)


# Получаем номер телефона
@router.message(HRForm.get_phone)
async def phone_question(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.update_data(tg=f"https://t.me/{message.from_user.username}")
    await message.answer(
        text="Мы очень рады, что ты хочешь расти и развиваться вместе с нами!\n"
        "Мы свяжемся с тобой в ближайшее время. А пока предлагаем заглянуть на наш сайт https://comfortel.pro "
        "и ознакомиться с актуальными вакансиями https://hh.ru/employer/965294?hhtmFrom=vacancy"
        "\nДо встречи!",
        reply_markup=ReplyKeyboardRemove(),
    )
    user_data = await state.get_data()
    send_results_email(user_data)
    await state.clear()


# Отвечаем на некорректные ответы
@router.message()
async def echo_all(message: Message):
    await message.answer(text="Что-то пошло не так...\n" "Воспользуйся клавиатурой бота")
    await message.delete()