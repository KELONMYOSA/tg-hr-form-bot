from io import BytesIO

from aiogram import Bot, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from src.keyboard import make_row_keyboard, request_contact_keyboard
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
        "1. B2B Продажи\n"
        "2. Техническая поддержка\n"
        "3. Разработка\n"
        "4. Инфраструктура, сети\n"
        "5. Управление проектами (телеком, IT)\n"
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
            "Не стесняйся, пиши рекрутеру компании Анне Кучер в tg - @kucher_hr. "
            "В сообщении укажи примерные даты практики/стажировки и 3 навыка, которые хочешь на ней получить."
        )
        await message.answer(
            text="Или ты можешь сейчас отправить свое резюме через бота. Отправить?",
            reply_markup=make_row_keyboard(["Да, отправить", "Пропустить"]),
        )
        await state.set_state(HRForm.resume_question)
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
            "указав 3 причины, по которым ты хочешь работать именно у нас."
        )
        await message.answer(
            text="Или ты можешь сейчас отправить свое резюме через бота. Отправить?",
            reply_markup=make_row_keyboard(["Да, отправить", "Пропустить"]),
        )
        await state.set_state(HRForm.resume_question)
    elif message.text == "Нет":
        await state.update_data(full_time="Нет")
        await message.answer(
            text="Ты можешь сейчас отправить свое резюме через бота. Отправить?",
            reply_markup=make_row_keyboard(["Да, отправить", "Пропустить"]),
        )
        await state.set_state(HRForm.resume_question)
    else:
        await message.answer(
            text="Ты заинтересован в стажировке/практике?", reply_markup=make_row_keyboard(["Да", "Нет"])
        )
        await state.set_state(HRForm.internship_question)


# Получение ответа на вопрос о резюме
@router.message(HRForm.resume_question, F.text.in_(["Да, отправить", "Пропустить"]))
async def resume_answer(message: Message, state: FSMContext):
    if message.text == "Да, отправить":
        await message.answer(
            text="Отправь следующим сообщением файл с резюме (pdf, docx, doc):",
            reply_markup=make_row_keyboard(["Пропустить"]),
        )
        await state.set_state(HRForm.get_resume)
    else:
        await message.answer(
            text="А теперь финальный этап!\nНапиши свой контактный телефон в формате +7 ХХХ ХХХ-ХХ-ХХ "
            'или нажми кнопку "Поделиться контактом"',
            reply_markup=request_contact_keyboard(),
        )
        await state.set_state(HRForm.get_phone)


# Получение файла резюме
@router.message(HRForm.get_resume)
async def resume_processing(message: Message, state: FSMContext, bot: Bot):
    if message.text == "Пропустить":
        await message.answer(
            text="А теперь финальный этап!\nНапиши свой контактный телефон в формате +7 ХХХ ХХХ-ХХ-ХХ "
            'или нажми кнопку "Поделиться контактом"',
            reply_markup=request_contact_keyboard(),
        )
        await state.set_state(HRForm.get_phone)
        return

    if not message.document or message.document.file_name.split(".")[-1].lower() not in ["pdf", "docx", "doc"]:
        await message.answer(
            text="Что-то тут не так...\n"
            'Отправь следующим сообщением файл с резюме (pdf, docx, doc) или нажми "Пропустить":'
        )
        return

    file_buf = BytesIO()
    await bot.download(message.document, file_buf)
    file_buf.seek(0)
    file_bytes = file_buf.read()

    await state.update_data(resume_name=message.document.file_name)
    await state.update_data(resume_bytes=file_bytes)

    await message.answer(
        text="А теперь финальный этап!\nНапиши свой контактный телефон в формате +7 ХХХ ХХХ-ХХ-ХХ "
        'или нажми кнопку "Поделиться контактом"',
        reply_markup=request_contact_keyboard(),
    )
    await state.set_state(HRForm.get_phone)


# Получаем номер телефона
@router.message(HRForm.get_phone)
async def phone_question(message: Message, state: FSMContext):
    if message.contact:
        await state.update_data(phone=message.contact.phone_number)
    else:
        await state.update_data(phone=message.text)

    if message.from_user.username:
        await state.update_data(tg=f"https://t.me/{message.from_user.username}")
    else:
        await state.update_data(tg=message.from_user.url)

    await message.answer(
        text="Мы очень рады, что ты хочешь расти и развиваться вместе с нами! Ждем твоего сообщения.\n"
        "А пока предлагаем заглянуть на наш сайт https://comfortel.pro  и познакомиться с актуальными вакансиями "
        "https://hh.ru/employer/965294?hhtmFrom=vacancy\n"
        "До встречи!",
        reply_markup=ReplyKeyboardRemove(),
    )
    user_data = await state.get_data()
    send_results_email(user_data)
    await state.clear()
    await state.set_state(HRForm.finished)


# Сообщение, если пользователь уже отправил анкету
@router.message(HRForm.finished)
async def finished_msg(message: Message):
    await message.delete()
    await message.answer(
        text="У тебя остались еще вопросы?\n"
        "Ты можешь связаться с рекрутером Комфортел - Анной Кучер в tg @kucher_hr",
        reply_markup=ReplyKeyboardRemove(),
    )


# Отвечаем на некорректные ответы
@router.message()
async def echo_all(message: Message, state: FSMContext):
    await message.delete()
    await message.answer(
        text="Что-то пошло не так...",
        reply_markup=make_row_keyboard(["Начать сначала"]),
    )
    await state.set_state(HRForm.restart)
