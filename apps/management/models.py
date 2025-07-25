from django.db import models

from apps.user.models import User
from apps.school import models

# Create your models here.
class Administrator(models.Model):
	user = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		verbose_name = "administrador",
		related_name="adminList",
	)

	school = models.ForeignKey(
		models.School,
		on_delete=models.CASCADE,
		related_name="adminSchoolList",
	)

	class Meta:
		verbose_name = "Adminstrador"
		verbose_name_plural = "Adminstradores"
		db_table = "administrator"


	def __str__(self):
		return f"Administradores de la escuela: [{self.school.name}]"

	def __repr__(self):
		return f"Administrator(id = {self.id}, school = {self.school.name}, user = {self.user.name})"