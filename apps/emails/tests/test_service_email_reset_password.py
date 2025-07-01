from unittest.mock import patch
from django.test import TestCase

from django.template.loader import render_to_string

from apps.emails.services.reset_password import EmailResetPassword

class ServiceEmailResetPasswordTest(TestCase):
	def setUp(self):
		self.template_name = 'reset_user_password.html'

	def test_create_email_reset_password(self):
		"""
			Validar creear un email para restablecer la contraseña
		"""
		context_user = {
			"name_user": "freddy",
			"password": "12345678"
		}
		emails_to = ["carlos@gmail.com"]
		template = render_to_string(f"emails/{self.template_name}",
			{"name": context_user['name_user'], "password": context_user['password']}
		)
		
		email_reset_password = EmailResetPassword(
			data_message = context_user,
			emails_to = emails_to
		)

		self.assertHTMLEqual(template, email_reset_password.content_message)
		self.assertEqual(email_reset_password.email.to, emails_to)

	def test_create_email_reset_password_without_name_user(self):
		"""
			Generar un error por no pasar 'name_user' en el 'data_message'
		"""

		context_user = {
			"password": "12345678"
		}
		emails_to = ["carlos@gmail.com"]

		message_error = "Por favor, debe pasar en data_message el 'name_user' con el nombre de usuario"

		with self.assertRaisesMessage(ValueError, message_error):
			email_reset_password = EmailResetPassword(
				data_message = context_user,
				emails_to = emails_to
			)

	def test_create_email_reset_password_without_password(self):
		"""
			Generar un error por no pasar 'password' en el 'data_message'
		"""

		context_user = {
			"name_user": "freddy"
		}
		emails_to = ["carlos@gmail.com"]

		message_error = "Por favor, debe pasar en data_message el 'password' con la contraseña restablecida"

		with self.assertRaisesMessage(ValueError, message_error):
			email_reset_password = EmailResetPassword(
				data_message = context_user,
				emails_to = emails_to
			)

	def test_create_email_reset_password_with_wrong_data_message(self):
		"""
			Generar un error por pasar un formato incorrecto en data_message
		"""
		context_user = ["freddy", "12345678"]
		emails_to = ["carlos@gmail.com"]

		message_error = "El 'data_message' debe ser de tipo 'dict'"
		
		with self.assertRaisesMessage(ValueError, message_error):
			email_reset_password = EmailResetPassword(
				data_message = context_user,
				emails_to = emails_to
			)

	
	def test_create_email_reset_password_without_emails_to(self):
		"""
			Genearar un error por no pasar una lista de emails de destino
		"""
		context_user = {
			"name_user": "freddy",
			"password": "12345678"
		}

		message_error = "Debe pasar un correo en lista de 'emails_to'"

		with self.assertRaisesMessage(ValueError, message_error):
			email_reset_password = EmailResetPassword(
				data_message = context_user,
			)

	def test_create_email_reset_password_with_wrong_format_emails_to(self):
		"""
			Genear un error por pasar los emails de destino en formato incorrecto
		"""

		context_user = {
			"name_user": "freddy",
			"password": "12345678"
		}
		emails_to = "carlos@gmail.com"

		message_error = "Debes pasar una lista o tupla con los correos"

		with self.assertRaisesMessage(ValueError, message_error):
			email_reset_password = EmailResetPassword(
				data_message = context_user,
				emails_to = emails_to
			)


	def test_does_not_exist_template_for_reset_password(self):
		"""
			Generar un error por no encontrar el template por defecto de EmailResetPassword
		"""

		with patch.object(EmailResetPassword, "template_name") as mock_template:
			mock_template.return_value = "template_does_not_exist.html"

			context_user = {
				"name_user": "freddy",
				"password": "12345678"
			}
			emails_to = ["carlos@gmail.com"]

			message_error = f"El template definido para esta servicio no existe {mock_template}"

			with self.assertRaisesMessage(ValueError, message_error):
				email_reset_password = EmailResetPassword(
					data_message = context_user,
					emails_to = emails_to
				)


