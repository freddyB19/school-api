from django.test import TestCase

from .utils.utils import set_user


class DecoratorHandlerValidationErrorTest(TestCase):
	def setUp(self):
		self.user = {"name": "a" * 40, "age": 12}
	
	def test_decorator_with_errors(self):
		"""
			Capturar los errores del decorador y retornarlos
		"""
		result = set_user(user = self.user)

		self.assertEqual(result["status"], "error")
		self.assertIsInstance(result["details"], list)
		self.assertEqual(len(result["details"]), 2)


	def test_decorator_with_valida_data(self):
		"""
			Retornar los resultados esperados por lafunción
		"""
		self.user.update({"name": "Freddy", "age": 25})

		result = set_user(user = self.user)

		self.assertEqual(result["status"], "success")
		self.assertIsInstance(result["details"], dict)
		self.assertEqual(result["details"], self.user)





