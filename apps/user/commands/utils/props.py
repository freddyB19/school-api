from typing_extensions import Annotated

from pydantic import BaseModel, ValidationInfo, WrapValidator

from apps.utils.functions import validate_choice

from apps.user import models


def validate_length_name(value:str, handler, info: ValidationInfo) -> str:
	min_length_name = models.MIN_LENGTH_NAME
	max_length_name = models.MAX_LENGTH_NAME

	total_len_name = len(value)

	if total_len_name >= min_length_name and total_len_name <= max_length_name:
		return value

	message_error = f"La longitud debe ser entre {min_length_name} y {max_length_name} caracteres"
	message_error += f" en ({info.field_name})"

	raise ValueError(message_error)

def validate_length_password(value:str, handler, info: ValidationInfo) -> str:
	min_length_password = models.MIN_LENGTH_PASSWORD
	total_len_password = len(value)
	
	if total_len_password >= min_length_password:
		return value

	message_error = f"La contraseña es muy corta, debe ser mayor a {min_length_password} caractéres"

	raise ValueError(message_error)

def validate_existent_email(value:str, handler, info: ValidationInfo) -> str:
	if not models.User.objects.filter(email = value).exists():
		return value

	raise ValueError("Ya existe un usuario con este email")


def validate_choice_role(value:int, handler, info: ValidationInfo) -> int:
	if validate_choice(choice = value, options = models.TypeRole):
		return value

	message_error = f"La opción '{value}' es incorrecta"

	raise ValueError(message_error)


PropName = Annotated[str, WrapValidator(validate_length_name)]
PropEmail = Annotated[str, WrapValidator(validate_existent_email)]
PropPassword = Annotated[str, WrapValidator(validate_length_password)]
PropRole = Annotated[int, WrapValidator(validate_choice_role)]

class CreateUserParam(BaseModel):
	name: PropName
	email: PropEmail
	password: PropPassword

class UpdateUserParam(BaseModel):
	name: PropName | None = None
	email: PropEmail | None = None
	role: PropRole | None = None
	is_active: bool | None = None

class UpdatePasswordParam(BaseModel):
	password: PropPassword

