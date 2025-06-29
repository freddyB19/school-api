from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
"""
subject = "Restableciendo contraseña"
from_email = "freddy@gmail.com"
to = []

to.append(email)

html_content =  render_to_string(
	"emails/reset_user_password.html",
	context={"name": user_name, "password": plain_password}
)

email = EmailMultiAlternatives(
	subject,
	html_content,
	from_email, 
	to
)

email.content_subtype = "html"

try:
	email.send()
except Exception as e:
	raise e
"""


class ContentHTMLMessage:
	BASIC_TEMPLATE = "template_email_basic.html"
	
	
	@classmethod
	def set_message(cls, template_name:str = BASIC_TEMPLATE, context:dict = {}) -> str:
		if not template_name:
			raise ValueError("Debe indicar el nombre del template")

		if not template_name.endswith(".html"):
			raise ValueError("Debe ser archivo de html")

		if not isinstance(context, dict):
			raise ValueError("Debe pasar un diccionario con los valores para el template")


		template = f"emails/{template_name}"
		return render_to_string(
			template,
			context=context
		)

class ConfigEmail:
	SUBTYPE_TEXT = "text"
	SUBTYPE_HTML = "html"

	@classmethod
	def set_config(cls, subject:str, from_email:str, to: list[str] | tuple[str], content:str, subtype = SUBTYPE_TEXT) -> EmailMultiAlternatives:
		if subtype != cls.SUBTYPE_TEXT and subtype != cls.SUBTYPE_HTML:
			raise ValueError(f"Debe ser un subtype correcto: [{cls.SUBTYPE_TEXT} | {cls.SUBTYPE_HTML}]")
		if not to:
			raise ValueError("Debe pasar un email en lista de 'to' ")
		
		if not isinstance(to, list) and not isinstance(to, tuple):
			raise ValueError("Debes pasar una lista o tupla con los emails")

		email = EmailMultiAlternatives(
			subject,
			content,
			from_email, 
			to
		)

		email.content_subtype = subtype

		return email


class SendEmail:

	@classmethod
	def send(cls, email: EmailMultiAlternatives) -> None:
		if not isinstance(email, EmailMultiAlternatives):
			raise ValueError("Debe ser una instancia de: [ EmailMultiAlternatives ]")

		try:
			email.send()
		except Exception as e:
			raise e