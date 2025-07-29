from unittest.mock import (patch, Mock)

from django.test import TestCase

from apps.user.services.signals.signals import (
	reset_password,
	SignalResetPassword,

)

from apps.user.services.signals.receivers import (
	reset_password_receiver
)


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


