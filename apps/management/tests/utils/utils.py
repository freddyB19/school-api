import tempfile

from apps.management import models

from PIL import Image
from faker import Faker

faker = Faker(locale = "es")

def get_administrator(school_id: int = None):
	if not school_id:
		raise ValueError("Debe ser el ID de 'school'")

	try:
		return models.Administrator.objects.get(school_id = school_id)
	except models.Administrator.DoesNotExist as e:
		return None


def get_long_string():
	return f"{faker.paragraph(nb_sentences = 5)}{faker.paragraph(nb_sentences = 5)}"


def create_list_images() -> list:
	images = []
		
	for _ in range(3):
		temp_file = tempfile.NamedTemporaryFile(suffix = ".jpg")

		image = Image.new("RGB", (10, 10))
		image.save(temp_file, format="JPEG")
		temp_file.seek(0)
		
		images.append(temp_file)

	return images
