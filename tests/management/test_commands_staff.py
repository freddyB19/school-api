import unittest
from rest_framework import exceptions
from apps.school import models
from apps.management.apiv1.school import serializers
from tests import faker
from .utils import testcases, testcases_data


class CommandCreateStaffTest(testcases.BasicCommandTestCase):

	def setUp(self):
		super().setUp()

		self.add_staff = {
			"name": faker.text(max_nb_chars = models.MAX_LENGTH_SCHOOSTAFF_NAME),
			"occupation": faker.random_element(
				elements = models.OccupationStaff.values
			)
		}


	def test_create_staff(self):
		"""
			Validar agregar personal (administrativo/docente) a una escuela
		"""
		# Agregando personal docente
		self.add_staff.update({
			"occupation": models.OccupationStaff.teacher.value
		})

		serializer = serializers.MSchoolStaffRequest(
			data = self.add_staff,
			context = {"pk": self.school.id}
		)

		serializer.is_valid(raise_exception = True)

		staff = serializer.save()

		self.assertTrue(staff.id)
		self.assertEqual(staff.name, self.add_staff["name"])
		self.assertEqual(staff.occupation, self.add_staff["occupation"])


		# Agregando personal administrativo
		self.add_staff.update({
			"occupation": models.OccupationStaff.administrative.value
		})

		serializer = serializers.MSchoolStaffRequest(
			data = self.add_staff,
			context = {"pk": self.school.id}
		)

		serializer.is_valid(raise_exception = True)

		staff = serializer.save()

		self.assertTrue(staff.id)
		self.assertEqual(staff.name, self.add_staff["name"])
		self.assertEqual(staff.occupation, self.add_staff["occupation"])

	def test_create_staff_with_wrong_data(self):
		"""
			Generar un error por enviar datos invalidos
		"""
		test_case = testcases_data.CREATE_STAFF_WITH_WRONG_DATA

		for case in test_case:
			with self.subTest(case = case):

				serializer = serializers.MSchoolStaffRequest(
					data = case,
					context = {"pk": self.school.id}
				)

				with self.assertRaises(exceptions.ValidationError):
					serializer.is_valid(raise_exception = True)

	def test_create_staff_with_does_not_exist_school(self):
		"""
			Generar un error por pasar el ID de una escuela que no existe
		"""
		wrong_school_id = faker.random_int(min = self.school.id + 1)

		serializer = serializers.MSchoolStaffRequest(
			data = self.add_staff,
			context = {"pk": wrong_school_id}
		)

		serializer.is_valid(raise_exception = True)

		with self.assertRaises(exceptions.ValidationError):
			staff = serializer.save()