from functools import wraps
from typing import Optional

from pydantic import BaseModel
from pydantic import ValidationError
from pydantic import validate_call

from .result_commands import MessageError

def handle_validation_errors(func):
	validated_func = validate_call(func)

	@wraps(func)
	def wrapper(*args, **kwargs):
		try:
			return validated_func(*args, **kwargs)
		except ValidationError as e:
			#print(e.errors())
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
