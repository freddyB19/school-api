import random

from pydantic import validate_call, ConfigDict
from rest_framework import status as status_code

from apps.user import models
from apps.utils.result_commands import ResultCommand

from .utils.props import CreateUserParam


@validate_call(config = ConfigDict(hide_input_in_errors=True))
def create_user(user: CreateUserParam):

	return ResultCommand(
		query = models.User.objects.create_user(
			name = user.name,
			email= user.email,
			password = user.password,
		)
	)

@validate_call(config = ConfigDict(hide_input_in_errors=True))
def get_user(pk: int) -> ResultCommand:
	user =  models.User.objects.filter(pk = pk).first()

	if not user:
		return ResultCommand(
			status = False,
			errors = [{"message": f"No existe información para el usuario {pk}"}],
			error_code = status_code.HTTP_404_NOT_FOUND
		)

	return ResultCommand(
		status = True,
		query = user
	)

@validate_call(config = ConfigDict(hide_input_in_errors=True))
def change_password(new_password: str, pk: int) -> ResultCommand:

	user_exist = get_user(pk = pk)

	if not user_exist.status:
		return user_exist
	
	user = user_exist.query
	user.set_password(new_password)
	user.save()
	return ResultCommand(status = True)


@validate_call(config = ConfigDict(hide_input_in_errors=True))
def get_user_by_email(email: str) -> ResultCommand:

	user_exist = models.User.objects.filter(email = email)

	if not user_exist.exists():
		return ResultCommand(
			status = False,
			errors = [{"message": f"No existe un usuario con ese email: {email}"}],
			error_code = status_code.HTTP_404_NOT_FOUND
		)

	return ResultCommand(status = True, query = user_exist.first())

SIZE_PASSWORD_GENERATE = 12

@validate_call(config = ConfigDict(hide_input_in_errors=True))
def generate_password(size:int = SIZE_PASSWORD_GENERATE) -> ResultCommand:

	chars = "abcdefghijklmnñopqrstuvwxyz"
	symbols = "·|?¿¡,.:[]{}$#@!()/=;&%<>-_+*"
	numbers = "0123456789"
	
	string = chars + chars.upper() + numbers + symbols
	password = "".join(random.sample(string, size))

	return ResultCommand(status = True, query = password)