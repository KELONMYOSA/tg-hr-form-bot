from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


def request_contact_keyboard() -> ReplyKeyboardMarkup:
    row = [KeyboardButton(text="Поделиться контактом", request_contact=True)]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)
