import django.dispatch
from django.conf import settings
from apps.user.models import TypeRole, User

reset_password = django.dispatch.Signal()

change_role = django.dispatch.Signal()

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

class SignalChangeRole:

	def send(self, role:int = None, user:User = None):
		if role not in TypeRole.values:
			raise ValueError(f"Debe ser un role valido {TypeRole.choices}")

		if not isinstance(user, User):
			raise ValueError(f"Debe enviar un usuario, no un [{type(user)}] - {user}")



		change_role.send(sender=self.__class__, role = role, user = user)