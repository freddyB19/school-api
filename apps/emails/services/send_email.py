from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMultiAlternatives
from django.template.exceptions import TemplateDoesNotExist

class ContentHTMLMessage:
	BASIC_TEMPLATE = "template_email_basic.html"
	PATH_TEMPLATES = "emails/"
	
	@classmethod
	def set_message(cls, template_name:str = BASIC_TEMPLATE, context:dict = {}) -> str:
		try:
			path_template = f"{cls.PATH_TEMPLATES}{template_name}"
			template = get_template(path_template)
		except TemplateDoesNotExist as e:
			raise ValueError(f"No existe este template: {cls.PATH_TEMPLATES}{template_name}")

		if not template_name:
			raise ValueError("Debe indicar el nombre del template")

		if not template_name.endswith(".html"):
			raise ValueError("Debe ser archivo de html")

		if not isinstance(context, dict):
			raise ValueError("Debe pasar un diccionario con los valores para el template")

		
		template = f"{cls.PATH_TEMPLATES}{template_name}"
		
		return render_to_string(
			template,
			context=context
		)

class ConfigEmail:
	SUBTYPE_TEXT = "text"
	SUBTYPE_HTML = "html"
	SUBTYPES = [
		SUBTYPE_TEXT,
		SUBTYPE_HTML
	]
	SUBJECT = "De parte de Yetic"
	DEFAULT_CONTENT = "Gracias por considerar usar nuestro servicio"

	@classmethod
	def set_config(cls, subject:str = SUBJECT, from_email:str = None, to: list[str] | tuple[str] = [], content:str = DEFAULT_CONTENT, subtype = SUBTYPE_TEXT) -> EmailMultiAlternatives:
		if not from_email:
			raise ValueError(f"Debe indicar de parte de quien será enviado el email")
		if subtype not in cls.SUBTYPES:
			raise ValueError(f"Debe ser un subtype correcto: {cls.SUBTYPES}")
		if not to:
			raise ValueError("Debe pasar una lista correos distinatario(s)")
		
		if not isinstance(to, list) and not isinstance(to, tuple):
			raise ValueError("Debes pasar una lista o tupla con los correos destinatarios")

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
	def send(cls, email: EmailMultiAlternatives) -> int:
		if not isinstance(email, EmailMultiAlternatives):
			raise ValueError("Debe ser una instancia de: [ EmailMultiAlternatives ]")

		try:
			return email.send()
		except Exception as e:
			raise e