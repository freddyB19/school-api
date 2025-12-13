import uuid

from pydantic import validate_call, ConfigDict

FILE_FORMAT_LEN = 2
UNKNOWN_FILE_FORMAT = None


@validate_call(config = ConfigDict(hide_input_in_errors=True))
def set_name_file(file_name: str) -> str | None:
	format_file = file_name.split(".")

	if len(format_file) == FILE_FORMAT_LEN:

		ext = format_file[-1]

		return f"{uuid.uuid4()}.{ext}"

	return UNKNOWN_FILE_FORMAT
