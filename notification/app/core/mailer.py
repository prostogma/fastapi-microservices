from pathlib import Path
from email.message import EmailMessage

from jinja2 import Environment, FileSystemLoader

from aiosmtplib import SMTP

BASE_DIR = Path(__file__).resolve().parents[2]


class Mailer:
    def __init__(self, host: str, port: int, user: str):
        self.host = host
        self.port = port
        self.user = user

        # Настройка jinja2 (где лежат шаблоны)
        template_dir = str(BASE_DIR / "templates")
        self.env = Environment(loader=FileSystemLoader(template_dir))

    async def send_registration_email(self, recipient: str, token: str):
        template = self.env.get_template("registration.html")

        html_content = template.render(email=recipient, token=token, verify_url="...")

        message = EmailMessage()
        message["From"] = self.user or "noreply@example.com"
        message["To"] = recipient
        message["Subject"] = "Подтверждение регистрации"
        message.set_content(html_content, subtype="html")

        async with SMTP(hostname=self.host, port=self.port) as smtp:
            await smtp.send_message(message)


mailer = Mailer(host="localhost", port="1025", user="manager@site.ru")
