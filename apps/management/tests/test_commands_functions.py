from django.test import TestCase

from apps.management.commands.utils.functions import set_name_image

from . import faker

class SetImageNameTest(TestCase):

	def test_set_new_name_to_image(self):
		"""
			Cambiar el nombre de una imagen
		"""

		image = faker.file_name(category='image')

		result = set_name_image(image_name = image)

		self.assertTrue(result)
		self.assertNotEqual(image, result)

		ext_image = image.split(".")[-1]
		ext_result_image = result.split(".")[-1]
		
		self.assertEqual(ext_image, ext_result_image)

	def test_set_new_name_to_image_with_wrong_format(self):
		"""
			Devolviendo un 'None' por formato invalido de la imagen
		"""

		image = faker.file_name(extension = '')

		result = set_name_image(image_name = image)

		self.assertFalse(result)
	