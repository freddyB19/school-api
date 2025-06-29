import random
from typing import Optional

from pydantic import validate_call

from apps.user import models
from apps.utils.result_commands import ResultCommand
from apps.utils.decorators import handle_validation_errors

from .utils.props import (
	CreateUserParam,
	UpdateUserParam,
	UpdatePasswordParam,
	PropPassword
)

SIZE_PASSWORD_GENERATE = 12

@validate_call
def is_valid_email(email: str = None) -> ResultCommand:
	if not email:
		raise ValueError("Se necesita un valor para el parametro 'email'")

	return ResultCommand(
		query = models.User.objects.filter(email = email).exists()
	)

@handle_validation_errors
def create_user(user: CreateUserParam, errors: Optional[list] = None):
	if errors:
		return ResultCommand(status = False, errors = errors)

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
			errors = [{"message": f"No existe información para el usuario {pk}"}]
		)

@handle_validation_errors
def change_user(update: UpdateUserParam, pk: int = None, errors: Optional[list] = None) -> ResultCommand:
	if not pk:
		raise ValueError("Se necesita un valor tipo (int) para el parametro 'pk'")

	if errors:
		return ResultCommand(status = False, errors = errors)

	context = {
		"status": False,
		"errors": [{"message": f"No existe información para el usuario {pk}"}]
	}
	
	update_columns = update.model_dump(exclude_defaults = True)

	user = models.User.objects.filter(pk = pk).update(
		**update_columns
	)

	if user:
		context.update({
			"status": True,
			"errors": None,
			"query": models.User.objects.values(
				"id", 
				"name", 
				"role", 
				"email",
				"is_active"
			).get(pk = pk)
		})

	return ResultCommand(**context)

@handle_validation_errors
def change_password(new_password: PropPassword, pk: int = None, errors: Optional[list] = None) -> ResultCommand:
	if not pk:
		raise ValueError("Se necesita un valor tipo (int) para el parametro 'pk'")

	if errors:
		return ResultCommand(status = False, errors = errors)

	has_user = get_user(pk = pk)

	if not has_user.status:
		return has_user
	
	user = has_user.query
	user.set_password(new_password)
	user.save()
	return ResultCommand(status = True)


def generate_password() -> ResultCommand:
	size = SIZE_PASSWORD_GENERATE

	chars = "abcdefghijklmnñopqrstuvwxyz"
	simbols = "·|?¿¡,.:[]{}$#@!()/=;&%<>-_+*"
	numbers = "0123456789"
	
	string = chars + chars.upper() + numbers + simbols
	password = "".join(random.sample(string, size))

	return ResultCommand(status = True, query = password)