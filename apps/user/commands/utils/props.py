from typing_extensions import Annotated

from pydantic import BaseModel
from pydantic import TypeAdapter
from pydantic import ValidationInfo
from pydantic import WrapValidator

from apps.utils.functions import validate_choice

from apps.user import models
from apps.user.models import User
from apps.user.models import MAX_LENGTH_NAME
from apps.user.models import MIN_LENGTH_NAME
from apps.user.models import MIN_LENGTH_PASSWORD


UserModel = TypeAdapter(type[User])

def validate_length_name(value:str, handler, info: ValidationInfo) -> str:
	if len(value) >= MIN_LENGTH_NAME and len(value) <= MAX_LENGTH_NAME:
		return value

	message_error = f"La longitud debe ser entre {MIN_LENGTH_NAME} y {MAX_LENGTH_NAME} caracteres"
	message_error += f" en ({info.field_name})"

	raise ValueError(message_error)

def validate_length_password(value:str, handler, info: ValidationInfo) -> str:
	if len(value) >= MIN_LENGTH_PASSWORD:
		return value

	message_error = f"La contraseña es muy corta, debe ser mayor a {MIN_LENGTH_PASSWORD} caractéres"

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

