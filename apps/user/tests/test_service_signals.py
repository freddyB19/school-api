from unittest.mock import (patch, Mock)

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from django.test import TestCase

from apps.user.services.signals.signals import (
	reset_password,
	change_role,
	SignalChangeRole,
	SignalResetPassword,
)

from apps.user.models import TypeRole, User
from apps.user.services.signals.receivers import (
	change_role_receiver,
	reset_password_receiver
)

from .utils.utils import create_user, create_permissions


class UserServiceResetPassword(TestCase):
	
	def test_signal_reset_password_emits(self):
		"""
			Validar que el signal 'reset_password' es emitido
		"""
		with patch.object(reset_password, 'send') as mock_send:
			signal = SignalResetPassword()

			plain_password = "12345"
			name = "Freddy"	
			email = "fredd@example.com"			

			signal.send(plain_password = plain_password, name = name, email = email)

			mock_send.assert_called_once()
			mock_send.assert_called_once_with(
				sender = SignalResetPassword,
				plain_password = plain_password,
				name = name,
				email = email
			)

	
	def test_signal_reset_password_with_mock_receiver(self):
		"""
			Mockeando el receiver, validar que el receptor de 'reset_password' se ejecuta correctamente
		"""
		mock_receiver = Mock()

		reset_password.disconnect(reset_password_receiver, sender = SignalResetPassword)

		reset_password.connect(mock_receiver, sender = SignalResetPassword)

		plain_password = "12345"
		name = "Freddy"
		email = "fredd@example.com"	

		try:
			signal = SignalResetPassword()
	
			signal.send(plain_password = plain_password, name = name, email = email)

			mock_receiver.assert_called_once()
			mock_receiver.assert_called_once_with(
				sender = SignalResetPassword,
				plain_password = plain_password,
				name = name,
				email = email,
				signal = reset_password
			)
		finally:
			reset_password.connect(reset_password_receiver, sender = SignalResetPassword)


class UserServiceChangeRole(TestCase):

	def test_signal_change_role_emits(self):
		"""
			Validar que el signal 'change_role' es emitido
		"""

		with patch.object(change_role, 'send') as mock_send:
			signal = SignalChangeRole()
			
			role = TypeRole.admin
			user = create_user()

			signal.send(role = role, user = user)

			mock_send.assert_called_once()
			mock_send.assert_called_once_with(
				sender = SignalChangeRole,
				role = role,
				user = user,
			)

	def test_signal_change_role_with_wrong_params(self):
		"""
			Enviando parametros incorrectos al método send del signal
		"""
		test_cases = [
			{
				"values": {
					"role": TypeRole.admin,
					"user": 1
				},
				"expect": {
					"raise": ValueError,
					"message": "Debe enviar un usuario, no un [<class 'int'>] - 1" 
				}
			},
			{
				"values": {
					"role": 12,
					"user": create_user()
				},
				"expect": {
					"raise": ValueError,
					"message": f"Debe ser un role valido {TypeRole.choices}"
				}
			}
		]

		for case in test_cases:
			with self.subTest(case = case):
				signal = SignalChangeRole()

				with self.assertRaisesMessage(case['expect']['raise'], case['expect']['message'] ):
					signal.send(**case['values'])




	def test_signal_change_role_with_mock_receiver(self):
		"""
			Mockeando el receiver, validar que el receptor de 'change_role' se ejecuta correctamente
		"""
		create_permissions(codename = "can_change_user_role")

		mock_receiver = Mock()

		change_role.disconnect(change_role_receiver, sender = SignalChangeRole)

		change_role.connect(mock_receiver, sender = SignalChangeRole)

		role = TypeRole.admin
		user = create_user(role = 0)

		try:
			signal = SignalChangeRole()			

			signal.send(role = role, user = user)

			mock_receiver.assert_called_once()
			mock_receiver.assert_called_once_with(
				sender = SignalChangeRole,
				role = role,
				user = user,
				signal = change_role
			)
			
		finally:
			reset_password.connect(change_role_receiver, sender = SignalChangeRole)
