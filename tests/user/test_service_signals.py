from unittest.mock import patch, Mock

from apps.user.services.signals import signals, receivers

from tests import faker

from apps.user import models
from apps.user.services.signals.utils import exceptions

from .utils.testcases import ServiceTestCase
from .utils.utils import create_user, create_permissions

class UserServiceResetPassword(ServiceTestCase):
	
	def test_signal_reset_password_emits(self):
		"""
			Validar que el signal 'reset_password' es emitido
		"""
		with patch.object(signals.reset_password, 'send') as mock_send:
			signal = signals.SignalResetPassword()

			plain_password = faker.password()
			name = faker.name()
			email = fa		

			signal.send(plain_password = plain_password, name = name, email = email)

			mock_send.assert_called_once()
			mock_send.assert_called_once_with(
				sender = signals.SignalResetPassword,
				plain_password = plain_password,
				name = name,
				email = email
			)

	
	def test_signal_reset_password_with_mock_receiver(self):
		"""
			Mockeando el receiver, validar que el receptor de 'reset_password' se ejecuta correctamente
		"""
		mock_receiver = Mock()

		signals.reset_password.disconnect(
			receivers.reset_password_receiver, 
			sender = signals.SignalResetPassword
		)

		signals.reset_password.connect(
			mock_receiver, 
			sender = signals.SignalResetPassword
		)

		plain_password = faker.password()
		name = faker.name()
		email = faker.email()

		try:
			signal = signals.SignalResetPassword()
	
			signal.send(
				plain_password = plain_password, 
				name = name, email = email
			)

			mock_receiver.assert_called_once()
			
			mock_receiver.assert_called_once_with(
				sender = signals.SignalResetPassword,
				plain_password = plain_password,
				name = name,
				email = email,
				signal = signals.reset_password
			)
		finally:
			signals.reset_password.connect(
				receivers.reset_password_receiver, 
				sender = signals.SignalResetPassword
			)


class UserServiceChangeRole(ServiceTestCase):

	def test_signal_change_role_emits(self):
		"""
			Validar que el signal 'change_role' es emitido
		"""

		with patch.object(signals.change_role, 'send') as mock_send:
			signal = signals.SignalChangeRole()
			
			role = models.TypeRole.admin
			user = create_user()

			signal.send(role = role, user = user)

			mock_send.assert_called_once()
			mock_send.assert_called_once_with(
				sender = signals.SignalChangeRole,
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
					"role": models.TypeRole.admin,
					"user": 1
				},
				"expect": {
					"raise": exceptions.InvalidValue,
					"message": exceptions.ERROR_MESSAGE_INVALID_VALUE 
				}
			},
			{
				"values": {
					"role": 12,
					"user": create_user()
				},
				"expect": {
					"raise": exceptions.InvalidUserRole,
					"message": exceptions.ERROR_MESSAGE_INVALID_ROLE
				}
			}
		]

		for case in test_cases:
			with self.subTest(case = case):
				signal = signals.SignalChangeRole()

				error_type = case['expect']['raise']
				error_message = case['expect']['message']

				with self.assertRaisesMessage(error_type,  error_message):
					signal.send(**case['values'])


	def test_signal_change_role_with_mock_receiver(self):
		"""
			Mockeando el receiver, validar que el receptor de 'change_role' se ejecuta correctamente
		"""
		create_permissions(codename = "can_change_user_role")

		mock_receiver = Mock()

		signals.change_role.disconnect(
			receivers.change_role_receiver, 
			sender = signals.SignalChangeRole
		)

		signals.change_role.connect(mock_receiver, sender = signals.SignalChangeRole)

		role = models.TypeRole.admin
		user = create_user(role = 0)

		try:
			signal = signals.SignalChangeRole()			

			signal.send(role = role, user = user)

			mock_receiver.assert_called_once()
			mock_receiver.assert_called_once_with(
				sender = signals.SignalChangeRole,
				role = role,
				user = user,
				signal = signals.change_role
			)
			
		finally:
			signals.reset_password.connect(
				receivers.change_role_receiver, 
				sender = signals.SignalChangeRole
			)
