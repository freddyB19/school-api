from typing import TypeVar

from django.core.files.uploadedfile import InMemoryUploadedFile

from pydantic import validate_call, ConfigDict

from faker import Faker

from apps.utils.result_commands import ResultCommand

faker = Faker(locale="es")

UploadedFile = TypeVar("UploadedFile", bound=InMemoryUploadedFile)


@validate_call(config = ConfigDict(hide_input_in_errors=True, arbitrary_types_allowed = True))
def update_school_logo(image:InMemoryUploadedFile = None) -> ResultCommand:
	context = {
		"status": False,
	}

	if not image:
		context.update({"errors": ["Debe pasar una imagen"]})
	
	# Conectarme a un servicio para subir la imagen

	context.update({"query": faker.image_url(), "status": True})

	return ResultCommand(**context)