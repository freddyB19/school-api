import uuid

from pydantic import validate_call, ConfigDict

IMAGE_FORMAT_LEN = 2
UNKNOWN_IMAGE_FORMAT = None


@validate_call(config = ConfigDict(hide_input_in_errors=True))
def set_name_image(image_name: str) -> str | None:
	format_image = image_name.split(".")

	if len(format_image) == IMAGE_FORMAT_LEN:

		ext = format_image[-1]

		return f"{uuid.uuid4()}.{ext}"

	return UNKNOWN_IMAGE_FORMAT
