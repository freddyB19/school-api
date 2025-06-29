from rest_framework import permissions

from apps.user.models import TypeRole

has_permissions = [
	TypeRole.admin
]

class IsRoleAdminOrReadOnly(permissions.BasePermission):
	message = "No tienes permisos para realizar esta operación"

	def has_permission(self, request, view):
		if request.method in permissions.SAFE_METHODS:
			return True

		return request.user.role in has_permissions

class AdminCannotChangeOwnRole(permissions.BasePermission):
	message = "Un admin no puede cambiar de role"


	def has_permission(self, request, view):
		if request.method in permissions.SAFE_METHODS:
			return True

		pk = view.kwargs.get("pk")

		return request.user.role in has_permissions and request.user.id != pk



class IsUserOrReadOnly(permissions.BasePermission):
	message = "No tienes los permisos suficientes para acceder a esta información"

	def has_object_permission(self, request, view, obj):

		if request.user.role in has_permissions:
			return True

		return request.user.id == obj.id

class IsValidRequestUpdateUser(permissions.BasePermission):
	message = "Esta operación no se puede realizar este tipo de cambios: [role | password]"

	def has_permission(self, request, view):
	
		if request.method in permissions.SAFE_METHODS:
			return True

		data_request = request.data.keys()

		return "role" not in data_request and "password" not in data_request