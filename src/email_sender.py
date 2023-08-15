import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EmailSender:

    def __init__(self, user, password) -> None:
        self.user = user
        self.password = password

    def send_email(self, user_target, subject, body):

        server = self._get_email_server()
        email_message = self._build_email_message(user_target, subject, body)
        self._send_email(server, user_target, email_message)
        server.quit()

    def _get_email_server(self):
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.login(self.user, self.password)
        return server

    def _build_email_message(self, user_target: str, subject: str, body: str) -> str:
        email_message = MIMEMultipart()

        email_message['From'] = self.user
        email_message['To'] = user_target
        email_message['Subject'] = subject

        email_message.attach(MIMEText(body, 'plain'))

        email_message = email_message.as_string()

        return email_message

    def _send_email(self, server, user_target, email_message):
        server.starttls()
        server.sendmail(self.user, user_target, email_message)
