from apps.management import models

def get_administrator(school_id: int = None):
	if not school_id:
		raise ValueError("Debe ser el ID de 'school'")

	try:
		return models.Administrator.objects.get(school_id = school_id)
	except models.Administrator.DoesNotExist as e:
		return None