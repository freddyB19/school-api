import datetime, base64

from django.core.files.uploadedfile import SimpleUploadedFile

from tests import faker

from apps.management import models
from apps.school import models as school_models

def get_administrator(school_id: int = None):
	if not school_id:
		raise ValueError("Debe ser el ID de 'school'")
	try:
		return models.Administrator.objects.get(school_id = school_id)
	except models.Administrator.DoesNotExist as e:
		return None


def get_long_string():
	return f"{faker.paragraph(nb_sentences = 5)}{faker.paragraph(nb_sentences = 5)}"


def create_list_images(size:int = 1) -> list:
	images = [
		faker.file_name(category = 'image')
		for _ in range(size)
	]
	return images

def list_upload_images(size: int = 1) -> list:
	content = base64.b64decode(
		b"R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
	)

	images = []
	
	for num in range(size):
		image = faker.file_name(category = 'image')

		_, ext = image.split(".")
		content_type = f"image/{ext}"
		images.append(
			SimpleUploadedFile(
				image, 
				content=content, 
				content_type=content_type
			)
		)

	return images


def set_time(hour: int, minute: int) -> str:
	TIME_FORMAT = '%H:%M:%S'

	return datetime.time(hour = hour, minute = minute).strftime(TIME_FORMAT)

def set_daysweek(days:list[int | str] = [1,2,3,4,5], length:int = 4) -> list[int]:
	return faker.random_elements(
		length=length, 
		unique=True,
		elements=days
	)


def selected_daysweek_to_names(selected: list[int]) -> list[str]:
	"""
		Convierte la lista de enteros [1 - 5] en su correspondiente
		día de la semana.
	"""
	
	days_dict = {day.value: str(day.name) for day in school_models.DaysNumber}
	
	daysweek_names = [days_dict[day] for day in selected]

	return [school_models.DaysName[day].value for day in daysweek_names]


def set_format_dasyweek_query(selected: list[int]) -> str:
	"""
	Convertimos los días seleccionados en un formato
	valido para la 'query'
	[1,4,6] --> '1,4,6'
	"""
	selected_daysweek_to_str = [str(day) for day in selected]

	return ",".join(selected_daysweek_to_str)