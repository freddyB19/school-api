from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from .manager import UserManager
# Create your models here.

MAX_LENGTH_NAME = 100
MIN_LENGTH_NAME = 4

MIN_LENGTH_PASSWORD = 8

MAX_LENGTH_EMAIL = 100

class TypeRole(models.IntegerChoices):
	admin = 0,
	staff = 1

class User(AbstractBaseUser, PermissionsMixin):
	name = models.CharField(max_length = MAX_LENGTH_NAME, default = "Anon")
	email = models.EmailField(max_length = MAX_LENGTH_EMAIL, unique = True)
	role = models.IntegerField(
		choices = TypeRole,
		default = TypeRole.staff
	)

	date_joined = models.DateTimeField(auto_now_add = True)
	last_login = models.DateTimeField(auto_now_add = True)

	is_admin = models.BooleanField(default = False)
	is_staff = models.BooleanField(default = False)
	is_active = models.BooleanField(default = True)
	is_superadmin = models.BooleanField(default = False)

	objects = UserManager()

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['name']


	def __str__(self):
		return self.email

	def __repr__(self):
		return f"User(id = {self.id}, name = {self.name}, email = {self.email}, role = {self.role}, is_active = {self.is_active}, is_admin = {self.is_admin}, is_staff = {self.is_staff})"


	class Meta:
		verbose_name = "Usuario"
		verbose_name_plural = "Usuarios"
		indexes = [
			models.Index(fields = ["email"], name="email_user_idx")
		]