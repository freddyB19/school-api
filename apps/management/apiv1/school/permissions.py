from rest_framework import permissions


class IsUserPermission(permissions.DjangoModelPermissions):
	message = "Este usuario no posee los permisos necesarios para realizar esta operación" 