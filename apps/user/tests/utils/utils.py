from faker import Faker

from apps.user import models
from rest_framework.test import APIClient


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
