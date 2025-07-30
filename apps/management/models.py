from django.db import models
from django.urls import reverse

from apps.user.models import User
from apps.school.models import School

# Create your models here.
class Administrator(models.Model):
	users = models.ManyToManyField(User)

	school = models.ForeignKey(
		School,
		on_delete=models.CASCADE,
		related_name="adminSchoolList",
	)

	class Meta:
		verbose_name = "Adminstrador"
		verbose_name_plural = "Adminstradores"
		db_table = "administrator"

	def get_absolute_url(self):
		return reverse(
			"management:administrator-detail", 
			kwargs = {"pk": self.id}
		)


	def __str__(self):
		return f"Administradores de la escuela: [{self.school.name}]"

	def __repr__(self):
		return f"Administrator(id = {self.id}, school = {self.school.name}"