from functools import wraps
from typing import Optional

from pydantic import BaseModel, ConfigDict, ValidationError, validate_call

from .result_commands import MessageError

def handler_validation_errors(func):
	validated_func = validate_call(func, config = ConfigDict(
		hide_input_in_errors=True, arbitrary_types_allowed = True
		)
	)

	@wraps(func)
	def wrapper(*args, **kwargs):
		try:
			return validated_func(*args, **kwargs)
		except ValidationError as e:
			original_func = func
			list_errors = [
				MessageError(
					field = error.get("loc")[::-1][0],
					message = error.get("msg").replace("Value error,", "").strip()
				)
				for error in e.errors()
			]
			return original_func(*args, **kwargs, errors=list_errors)
	
	return wrapper
