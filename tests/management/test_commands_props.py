import random

from django.test import TestCase

from apps.management.commands.utils.props import INVALID_CHOICES_DAY

class ManagementCommandsProp(TestCase):
	"""
		Este test se encarga de validar que nuestra función 'INVALID_CHOICES_DAY'

		Los días de la semana son calificados en números, partiendo:
		desde 1 hasta el 5.

		[ Lunes = 1, Martes = 2, Miércoles = 3, Jueves = 4, Viernes = 5 ]

		Filtra todos los números menores a 1 y mayores a 5.
	"""
	
	def test_validate_filter_daysweek(self):
		"""
			Validar filtrado de dias de la semana
		"""
		valid_choices = [1,2,3,4,5]

		daysweek = random.choices(valid_choices, k = 3)

		result = INVALID_CHOICES_DAY(daysweek = daysweek)

		self.assertFalse(result)
		self.assertEqual(len(result), 0)


	def test_validate_filter_daysweek_with_wrong_choices(self):
		"""
			Validar que retorne los días que no cumplen con el criterio
			(day < 1) o (day > 5)
		"""
		invalid_choices = [6,7,8,10,9]
		daysweek = random.choices(invalid_choices, k = 3)

		result = INVALID_CHOICES_DAY(daysweek = daysweek)

		self.assertTrue(result)
		self.assertGreaterEqual(len(result), 1)
