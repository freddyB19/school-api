from django.db.models import Subquery
from django.db.models.base import ModelBase

from rest_framework import permissions

from apps.management import models
from apps.school import models as school_models

class IsUserPermission(permissions.DjangoModelPermissions):
	message = "Este usuario no posee los permisos necesarios para realizar esta operación" 



class BelongToOurAdministrator(permissions.BasePermission):
	"""
		Este permiso sirve para limitar que solo se pueda acceder/modificar
		la información del colegio al que formamos parte como administradores.
	"""
	message = "No tienes permisos para (acceder o modificar) información que no te pertenece"
	
	def has_permission(self, request, view):

		school_id = view.kwargs.get("pk")

		admin_school = models.Administrator.objects.filter(
			school_id = school_id,
			users__id = request.user.id
		).exists()

		return admin_school


def get_detail_data(model: ModelBase, id: int) -> dict[str, int]:
	
	return model.objects.filter(pk = id).values("school_id")


IMPLEMENTATION_ERROR = "Debe definir la instancia del modelo para: 'model'"

class BasePermissionDetailObject(permissions.BasePermission):
	"""
		Este permiso sirve para limitar que solo se pueda acceder/eliminar/modificar
		la información del colegio al que formamos parte como administradores.
	"""
	model = None
	message = "No tienes permisos para (acceder, modificar o eliminar) información que no te pertenece"
	
	def has_perm_detail(self, data_id:int, user_id:int):
		
		if not isinstance(getattr(self, 'model'), ModelBase):
			raise NotImplementedError(IMPLEMENTATION_ERROR)

		return models.Administrator.objects.filter(
			school_id__in = Subquery(
				get_detail_data(model = self.model, id = data_id)
			), 
			users__id = user_id
		).exists()

	def has_permission(self, request, view):

		data_id = view.kwargs.get("pk")
		user_id = request.user.id

		return self.has_perm_detail(data_id = data_id, user_id = user_id)


class CoordinatePermissionDetail(BasePermissionDetailObject):
	model = school_models.Coordinate


class SocialMediaPermissionDetail(BasePermissionDetailObject):
	model = school_models.SocialMedia


class CalendarPermissionDetail(BasePermissionDetailObject):
	model = school_models.Calendar


class OfficeHourPermissionDetail(BasePermissionDetailObject):
	model = school_models.OfficeHour


class NewsPermissionDetail(BasePermissionDetailObject):
	model = school_models.News


class StaffPermissionDetail(BasePermissionDetailObject):
	model = school_models.SchoolStaff


class GradePermissionDetail(BasePermissionDetailObject):
	model = school_models.Grade
