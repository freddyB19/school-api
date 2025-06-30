import os

from dotenv import load_dotenv
load_dotenv()

from .send_email import SendEmail
from .send_email import ConfigEmail
from .send_email import ContentHTMLMessage


class EmailResetPassword:
	from_email = os.getenv("EMAIL_HOST_USER")
	subject = "Restableciendo contraseña"
	
	def __init__(self, user_name:str, plain_password:str,  emails_to: list[str] | tuple[str] = []) -> None:
		if not isinstance(emails_to, list) or not isinstance(emails_to, tuple):
			raise ValueError("Debes pasar una lista o tupla con los emails")
		if not emails_to:
			raise ValueError("Debe pasar un email en lista de 'emails_to' ")

		self.user_name = user_name
		self.plain_password = plain_password
		self.emails_to = emails_to

		self.content_message = ContentHTMLMessage.set_message(
			template_name = "reset_user_password.html", 
			context = {"name": self.user_name, "password": self.plain_password}
		)

		self.email = ConfigEmail.set_config(
			subject = self.subject,
			from_email = self.from_email,
			to = self.emails_to,
			content = self.content_message,
			subtype = "html"
		)

	def send(self) -> None:
		SendEmail.send(email = self.email)

"""
	def set_content_message(self) -> str:
		return render_to_string(
			"emails/reset_user_password.html",
			context={"name": self.user_name, "password": self.plain_password}
		)

	def set_config_email(self) -> EmailMultiAlternatives:
		content = self.set_content_message()

		email = EmailMultiAlternatives(
			self.subject,
			content,
			self.from_email, 
			self.emails_to
		)

		email.content_subtype = "html"

		return email

	def send_email(self):
		email = self.set_config_email(emails_to = self.emails_to)

		try:
			email.send()
		except Exception as e:
			raise e
"""