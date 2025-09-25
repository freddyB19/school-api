from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

import factory

from tests import faker

from apps.user import models

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


class UserFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = models.User

	name = factory.LazyAttribute(lambda x: faker.name())
	email = factory.LazyAttribute(lambda x: faker.email())
	password = factory.LazyAttribute(lambda x: faker.password())

	@classmethod
	def _create(cls, model_class, *args, **kwargs):
		manager = cls._get_manager(model_class)
		
		return manager.create_user(*args, **kwargs)



def create_user(**kwargs) -> models.User:
	return UserFactory.create(**kwargs)


def bulk_create_user(size: int = 1) -> models.User:
	
	"""
		Nos permite crear multiples usuarios en una sola consulta

		Argumentos:
		size --> (int) Total de usuarios que van ha ser creados

		Retorno:
		Lista de usuarios creados
	"""
	return UserFactory.create_batch(size = size, **kwargs)


def create_permissions(name:str = "Test permission", codename:str = "test_permission") -> None:
	content_type = ContentType.objects.get_for_model(models.User)
	permission = Permission.objects.create(
		name = name,
		codename= codename,
		content_type=content_type,
	)


def get_permissions(codenames: list[str] = []) -> Permission:
	return Permission.objects.filter(codename__in = codenames)
