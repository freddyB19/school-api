from unittest.mock import patch

from django.template.loader import render_to_string

from apps.emails.services.send_email import ContentHTMLMessage
from apps.emails.services.reset_password import EmailResetPassword

from tests import faker

from .utils import testcases


class RenderingEmailTemplateTest(testcases.RenderingEmailTemplateTestCase):

	def test_set_content_html_message(self):
		"""
			Validar que se genere el string del html del mensaje
		"""
		template_name = "reset_user_password.html"

		context = {"name": faker.name(), "password": faker.password()}

		find = f"""{context['name']}"""	

		reset_password_email_template = render_to_string(
			f"emails/{template_name}",
			context= context
		)

		content_html = ContentHTMLMessage.set_message(
			template_name = template_name,
			context = context
		)

		self.assertTrue(isinstance(content_html, str))
		self.assertHTMLEqual(content_html, reset_password_email_template)
		self.assertInHTML(find, content_html)
		

	def test_set_content_html_message_without_template(self):
		"""
			Validar que se genere el string del html del mensaje sin pasar el 'template' 
		"""
		context = {"name": faker.name(), "password": faker.password()}

		find = f"""{context['name'].capitalize()} """	

		content_html = ContentHTMLMessage.set_message(
			context = context
		)

		self.assertTrue(isinstance(content_html, str))
		self.assertHTMLEqual(content_html, self.basic_email_template)
		self.assertNotInHTML(find, content_html)


	def test_set_content_html_message_without_nothing(self):
		"""
			Validar que se genere el string del html sin enviar nada
		"""
		content_html = ContentHTMLMessage.set_message()

		self.assertTrue(isinstance(content_html, str))
		self.assertHTMLEqual(content_html, self.basic_email_template)

	
	def test_set_content_html_message_with_no_existent_template(self):
		"""
			Genearar un error por pasar un template que no existe
		"""
		template_name = "does_not_exist.html"
		error_message =  f"No existe este template: emails/{template_name}"
		
		with self.assertRaisesMessage(ValueError, error_message):
		
			content_html = ContentHTMLMessage.set_message(
				template_name = template_name
			)


class RenderingEmailResetPasswordTest(testcases.RenderingEmailTemplateResetPasswordTestCase):

	def test_create_email_reset_password(self):
		"""
			Validar creear un 'email' para restablecer la contraseña
		"""
		template = render_to_string(f"emails/{self.template_name}",

			{
				"name": self.context_user['name_user'], 
				"password": self.context_user['password']
			}
		)
		
		email_reset_password = EmailResetPassword(
			data_message = self.context_user,
			emails_to = self.emails_to
		)

		self.assertHTMLEqual(template, email_reset_password.content_message)
		self.assertEqual(email_reset_password.email.to, self.emails_to)

	def test_create_email_reset_password_without_name_user(self):
		"""
			Generar un error por no pasar 'name_user' en el 'data_message'
		"""

		self.context_user.pop('name_user')

		error_message = "Por favor, debe pasar en data_message el 'name_user' con el nombre de usuario"

		with self.assertRaisesMessage(ValueError, error_message):
			email_reset_password = EmailResetPassword(
				data_message = self.context_user,
				emails_to = self.emails_to
			)

	def test_create_email_reset_password_without_password(self):
		"""
			Generar un error por no pasar 'password' en el 'data_message'
		"""

		self.context_user.pop("password")

		error_message = "Por favor, debe pasar en data_message el 'password' con la contraseña restablecida"

		with self.assertRaisesMessage(ValueError, error_message):
			email_reset_password = EmailResetPassword(
				data_message = self.context_user,
				emails_to = self.emails_to
			)

	def test_create_email_reset_password_with_wrong_data_message(self):
		"""
			Generar un error por pasar un formato incorrecto en 'data_message'
		"""
		self.context_user = [faker.name(), faker.password()]

		error_message = "El 'data_message' debe ser de tipo 'dict'"
		
		with self.assertRaisesMessage(ValueError, error_message):
			email_reset_password = EmailResetPassword(
				data_message = self.context_user,
				emails_to = self.emails_to
			)

	
	def test_create_email_reset_password_without_emails_to(self):
		"""
			Genearar un error por no pasar una lista de 'emails' de destino
		"""
		error_message = f"Debe pasar un correo en lista de 'emails_to'"

		with self.assertRaisesMessage(ValueError, error_message):
			email_reset_password = EmailResetPassword(
				data_message = self.context_user,
			)

	def test_create_email_reset_password_with_wrong_format_emails_to(self):
		"""
			Genear un error por pasar los 'emails' de destino en formato incorrecto
		"""
		self.emails_to = faker.email()

		error_message = "Debes pasar una lista o tupla con los correos"

		with self.assertRaisesMessage(ValueError, error_message):
			email_reset_password = EmailResetPassword(
				data_message = self.context_user,
				emails_to = self.emails_to
			)


	def test_does_not_exist_template_for_reset_password(self):
		"""
			Generar un error por no encontrar el 'template' por defecto de EmailResetPassword
		"""

		with patch.object(EmailResetPassword, "template_name") as mock_template:
			mock_template.return_value = "template_does_not_exist.html"

			error_message = f"El template definido para esta servicio no existe {mock_template}"

			with self.assertRaisesMessage(ValueError, error_message):
				email_reset_password = EmailResetPassword(
					data_message = self.context_user,
					emails_to = self.emails_to
				)
