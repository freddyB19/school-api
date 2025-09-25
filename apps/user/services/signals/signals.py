from typing import TypeVar

import django.dispatch

from apps.user.models import TypeRole, User

from .utils.exceptions import (
	InvalidValue,
	InvalidParams,
	InvalidUserRole
)


UserM = TypeVar("UserM", bound = User)

change_role = django.dispatch.Signal()
reset_password = django.dispatch.Signal()



class SignalResetPassword:

	def send(self, plain_password:str = None, name:str = None, email:str = None):
		if not plain_password or not name or not email:
			raise InvalidParams()

		result = reset_password.send(
			sender=self.__class__, 
			plain_password = plain_password,
			name = name,
			email = email
		)

class SignalChangeRole:

	def send(self, role:int = None, user:UserM = None):
		if role not in TypeRole.values:
			raise InvalidUserRole()

		if not isinstance(user, User):
			raise InvalidValue(f"Debe enviar un usuario, no un [{type(user)}] - {user}")



		change_role.send(sender=self.__class__, role = role, user = user)