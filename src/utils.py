import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.config import settings

sphere_dict = {
    "1": "B2B Продажи",
    "2": "Техническая поддержка",
    "3": "Разработка",
    "4": "Инфраструктура, сети",
    "5": "Управление проектами (телеком, IT)",
    "6": "Финансы, бухгалтерия",
    "7": "HR, психология",
    "8": "PR, маркетинг, event, графический дизайн",
    "9": "Другое",
}


def send_results_email(user_data: dict):
    server = smtplib.SMTP(settings.EMAIL_SMTP_HOST, settings.EMAIL_SMTP_PORT)
    server.starttls()
    server.sendmail(settings.EMAIL_SENDER, settings.EMAIL_RECIPIENT, _user_data_to_mail(user_data))
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
    msg["From"] = settings.EMAIL_SENDER
    msg["To"] = settings.EMAIL_RECIPIENT
    msg["Subject"] = "Отклик из Телеграм-бота"
    msg.attach(MIMEText(text, "html"))

    if user_data.get("resume_name"):
        resume = MIMEApplication(user_data["resume_bytes"], Name=user_data["resume_name"])
        resume["Content-Disposition"] = f'attachment; filename="{user_data["resume_name"]}"'
        msg.attach(resume)

    return msg.as_string()
