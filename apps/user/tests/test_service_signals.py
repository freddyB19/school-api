from unittest.mock import patch
from unittest.mock import Mock
from django.test import TestCase

from apps.user.services.signals.signals import reset_password
from apps.user.services.signals.signals import SignalResetPassword
from apps.user.services.receivers import reset_password_receiver

class UserServiceResetPassword(TestCase):
	
	def test_signal_reset_password_emits(self):
		"""
			Validar que el signal 'reset_password' es emitido
		"""
		with patch.object(reset_password, 'send') as mock_send:
			signal = SignalResetPassword()

			plain_password = "12345"
			name = "Freddy"			

			signal.send(plain_password = plain_password, name = name)

			mock_send.assert_called_once()
			mock_send.assert_called_once_with(
				sender = SignalResetPassword,
				plain_password = plain_password,
				name = name
			)

	
	def test_signal_reset_password_with_mock_receiver(self):
		"""
			Mockeando el receiver, validar que el receptor de 'reset_password' se ejecuta correctamente
		"""
		mock_receiver = Mock()

		reset_password.disconnect(reset_password_receiver, sender = SignalResetPassword)

		reset_password.connect(mock_receiver, sender = SignalResetPassword)

		try:
			signal = SignalResetPassword()
			plain_password = "12345"
			name = "Freddy"			

			signal.send(plain_password = plain_password, name = name)

			mock_receiver.assert_called_once()
			mock_receiver.assert_called_once_with(
				sender = SignalResetPassword,
				plain_password = plain_password,
				name = name,
				signal = reset_password
			)
		finally:
			reset_password.connect(reset_password_receiver, sender = SignalResetPassword)