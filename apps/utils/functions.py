from typing import Any
from typing_extensions import Annotated

from enum import Enum
from pydantic import BeforeValidator

def is_enum(value: Enum) -> Enum:
	if not type(value) == type(Enum):
		raise ValueError("el tipo de dato debe ser un Enum")

	return value

IsEnum = Annotated[Any, BeforeValidator(is_enum)]


def validate_choice(choice: str, options: IsEnum) -> bool:
	choices = [option for option in options]

	if choice not in choices:
		return False
	return True