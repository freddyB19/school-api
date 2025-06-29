import django.dispatch
from django.conf import settings


reset_password = django.dispatch.Signal()

class SignalResetPassword:

	def send(self, plain_password:str = None, name:str = None, email:str = None):
		if not plain_password or not name or not email:
			raise ValueError("Debe pasar [plain_password, name, email]")

		result = reset_password.send(
			sender=self.__class__, 
			plain_password = plain_password,
			name = name,
			email = email
		)