
from pydantic import validate_call

from faker import Faker

from apps.utils.result_commands import ResultCommand

faker = Faker(locale="es")

def update_school_logo(image = None) -> ResultCommand:
	context = {
		"status": False,
	}

	# Conectarme a un servicio para subir la imagen

	context.update({"query": faker.image_url(), "status": True})

	return ResultCommand(**context)