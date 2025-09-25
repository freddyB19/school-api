import random
from typing import Optional

from pydantic import validate_call
from rest_framework import status as status_code

from apps.user import models
from apps.utils.result_commands import ResultCommand
from apps.utils.decorators import handler_validation_errors

from .utils.props import (
	CreateUserParam,
	UpdateUserParam,
	UpdatePasswordParam,
	PropPassword
)

SIZE_PASSWORD_GENERATE = 12


@handler_validation_errors
def create_user(user: CreateUserParam, errors: Optional[list] = None):
	if errors:
		return ResultCommand(
			status = False, 
			errors = errors, 
			error_code = status_code.HTTP_400_BAD_REQUEST
		)

	return ResultCommand(
		query = models.User.objects.create_user(
			name = user.name,
			email= user.email,
			password = user.password,
		)
	)

@validate_call
def get_user(pk: int = None) -> ResultCommand:

	if not pk:
		raise ValueError("Se necesita un valor tipo (int) para el parametro 'pk'")

	try:
		return ResultCommand(
			query = models.User.objects.get(pk = pk)
		)
	except models.User.DoesNotExist as e:
		return ResultCommand(
			status = False,
			errors = [{"message": f"No existe información para el usuario {pk}"}],
			error_code = status_code.HTTP_404_NOT_FOUND
		)


@handler_validation_errors
def change_password(new_password: PropPassword, pk: int = None, errors: Optional[list] = None) -> ResultCommand:
	if not pk:
		raise ValueError("Se necesita un valor tipo (int) para el parametro 'pk'")

	if errors:
		return ResultCommand(
			status = False, 
			errors = errors, 
			error_code = status_code.HTTP_400_BAD_REQUEST
		)

	has_user = get_user(pk = pk)

	if not has_user.status:
		return has_user
	
	user = has_user.query
	user.set_password(new_password)
	user.save()
	return ResultCommand(status = True)


@validate_call
def get_user_by_email(email: str = None) -> ResultCommand:
	if not email:
		raise ValueError("Se necesita un valor tipo (str) para el parametro 'email'")

	has_user = models.User.objects.filter(email = email)

	if not has_user.exists():
		return ResultCommand(
			status = False,
			errors = [{"message": f"No existe un usuario con ese email: {email}"}],
			error_code = status_code.HTTP_404_NOT_FOUND
		)

	return ResultCommand(status = True, query = has_user.first())


def generate_password(size:int = SIZE_PASSWORD_GENERATE) -> ResultCommand:

	chars = "abcdefghijklmnñopqrstuvwxyz"
	simbols = "·|?¿¡,.:[]{}$#@!()/=;&%<>-_+*"
	numbers = "0123456789"
	
	string = chars + chars.upper() + numbers + simbols
	password = "".join(random.sample(string, size))

	return ResultCommand(status = True, query = password)