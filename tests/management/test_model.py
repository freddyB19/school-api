import unittest

from django.test import TransactionTestCase
from django.core.exceptions import ValidationError

from apps.management import models

from tests.user.utils.utils import create_user
from tests.school.utils.utils import create_school

from .utils import testcases

class AdministratorModelTest(testcases.AdministratorModelTestCase):

	def test_create_administrator(self):
		"""
			Creando tabla de admis para una determinada escuela
		"""
		user = create_user()
		admin_site = models.Administrator.objects.create(school = self.school)

		admin_site.users.add(user)

		self.assertTrue(admin_site)
		self.assertEqual(admin_site.users.count(), 1)

	def test_create_administrator_without_users(self):
		"""
			Creando tabla de admins sin agregar usuarios
		"""
		admin_site = models.Administrator.objects.create(school = self.school)

		self.assertTrue(admin_site)
		self.assertEqual(admin_site.users.count(), 0)


	def test_create_administrator_without_school(self):
		"""
			Creando tabla de admins sin agregar una escuela
		"""
		user = create_user()

		with self.assertRaisesMessage(ValidationError, 'This field cannot be null.'):

			admin_site = models.Administrator()
			admin_site.full_clean()
			admin_site.save()
			
			admin_site.users.add(user)


	def test_update_administrator_delete_user(self):
		"""
			Eliminando un usuario de la lista de usuarios 'admins'
		"""
		admin_site = models.Administrator.objects.create(school = self.school)

		user_juan = create_user(email = "juan@example.com")
		user_carlos = create_user(email = "carlos@example.com")
		user_jose = create_user(email = "jose@example.com")

		list_users = [
			user_juan, 
			user_carlos, 
			user_jose
		]

		admin_site.users.set(list_users)

		self.assertEqual(len(list_users), admin_site.users.count())

		#admin_site.users.remove(user_jose)
		
		admin_site.users.filter(id = user_jose.id).delete()
		"""
			Ambas opciones funcionan de igual forma, esta última nos ofrece
			la ventaja de solo eliminar el registro con tan solo el ID del
			usuario.
		"""

		self.assertLess(admin_site.users.count(), len(list_users))









