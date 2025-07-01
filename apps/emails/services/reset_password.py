import os

from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import render_to_string, get_template

from dotenv import load_dotenv
load_dotenv()

from .send_email import SendEmail
from .send_email import ConfigEmail
from .send_email import ContentHTMLMessage


class EmailResetPassword:
	from_email = os.getenv("EMAIL_HOST_USER")
	subject = "Restableciendo contraseña"
	template_name = "reset_user_password.html"
	
	def __init__(self, data_message:dict = {},  emails_to: list[str] | tuple[str] = []) -> None:
		try:
			template = get_template(f"emails/{self.template_name}")
		except TemplateDoesNotExist as e:
			raise ValueError(f"El template definido para esta servicio no existe {self.template_name}")

		if not isinstance(data_message, dict):
			raise ValueError("El 'data_message' debe ser de tipo 'dict'")

		if not data_message.get("name_user", False):
			raise ValueError("Por favor, debe pasar en data_message el 'name_user' con el nombre de usuario")

		if not data_message.get("password", False):
			raise ValueError("Por favor, debe pasar en data_message el 'password' con la contraseña restablecida")

		if not isinstance(emails_to, list) and not isinstance(emails_to, tuple):
			raise ValueError("Debes pasar una lista o tupla con los correos")
		
		if not emails_to:
			raise ValueError("Debe pasar un correo en lista de 'emails_to'")

		self.emails_to = emails_to

		self.content_message = ContentHTMLMessage.set_message(
			template_name = self.template_name, 
			context = {"name": data_message['name_user'], "password": data_message['password']}
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