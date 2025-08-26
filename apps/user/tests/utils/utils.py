from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from faker import Faker

from apps.user import models



faker = Faker(locale="es")

EMAIL = faker.email()
NAME = faker.name()
ROLE = faker.random_element(elements = (
	models.TypeRole.admin, 
	models.TypeRole.staff
))
PASSWORD = faker.pystr_format()

class FakerCreateUser:
	def __init__(self) -> None:
		self.email = EMAIL
		self.name = NAME
		self.role = ROLE
		self.password = PASSWORD

def create_user(name:str = "Jose", email:str = "jose@gmail.com", password:str = "12345", role:int = 1) -> models.User:
	return models.User.objects.create_user(
		name = name,
		email = email,
		password = password,
		role = role
	)


def bulk_create_user(total_users: int = 5):
	"""
		Nos permite crear multiples usuarios en una sola consulta

		Argumentos:
		total_users --> (int) Total de usuarios que van ha ser creados

		Retorno:
		Lista de usuarios creados
	"""
	users = [
		 models.User(
		 	name = faker.name(),
		 	email = faker.email(),
		 	password = faker.pystr_format()
		 )
		for i in range(total_users)
	]

	return models.User.objects.bulk_create(users)


def create_permissions(name:str = "Test permission", codename:str = "test_permission") -> None:
	content_type = ContentType.objects.get_for_model(models.User)
	permission = Permission.objects.create(
		name = name,
		codename= codename,
		content_type=content_type,
	)


def get_permissions(codenames: list[str] = []) -> Permission:
	return Permission.objects.filter(codename__in = codenames)
