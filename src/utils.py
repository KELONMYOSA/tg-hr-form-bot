import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.config import settings

sphere_dict = {
    "1": "Разработка",
    "2": "Техническая поддержка",
    "3": "Инфраструктура, сети",
    "4": "Управление проектами (телеком, IT)",
    "5": "B2B Продажи",
    "6": "Финансы, бухгалтерия",
    "7": "HR, психология",
    "8": "PR, маркетинг, event, графический дизайн",
    "9": "Другое",
}


def send_results_email(user_data: dict):
    server = smtplib.SMTP(settings.EMAIL_SMTP_HOST, settings.EMAIL_SMTP_PORT)
    server.starttls()
    server.login(settings.EMAIL_LOGIN, settings.EMAIL_PASSWORD)
    server.sendmail(settings.EMAIL_LOGIN, settings.EMAIL_RECIPIENT, _user_data_to_mail(user_data))
    server.quit()


def _user_data_to_mail(user_data: dict) -> str:
    data_list = [
        f"Фамилия Имя: {user_data['name']}",
        f"Направление: {user_data['direction']}",
        f"Курс: {user_data['year']}",
        f"Сфера: {user_data['sphere']}",
        f"Стажировка/практика: {user_data['intern']}",
        f"Полный день: {user_data['full_time']}",
        f"Телефон: {user_data['phone']}",
        f"Telegram: <a href='{user_data['tg']}'>@{user_data['tg'].replace('https://t.me/', '')}</a>",
    ]
    msg = MIMEMultipart()
    text = "<pre>" + "\n".join(data_list) + "<pre>"
    msg["From"] = settings.EMAIL_LOGIN
    msg["To"] = settings.EMAIL_RECIPIENT
    msg["Subject"] = "Отклик из Телеграм-бота"
    msg.attach(MIMEText(text, "html"))

    return msg.as_string()
