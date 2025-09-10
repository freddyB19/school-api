from rest_framework import permissions

from apps.management import models

class IsUserPermission(permissions.DjangoModelPermissions):
	message = "Este usuario no posee los permisos necesarios para realizar esta operación" 



class BelongToOurAdministrator(permissions.BasePermission):
	"""
		Este permiso sirve para limitar que solo se pueda acceder/modificar
		la información del colegio al que formamos parte como administradores.
	"""
	message = "No tienes permisos de modificar información que no te pertenece"
	
	def has_permission(self, request, view):

		school_id = view.kwargs.get("pk")

		admin_school = models.Administrator.objects.filter(
			school_id = school_id,
			users__id = request.user.id
		).exists()

		return admin_school
