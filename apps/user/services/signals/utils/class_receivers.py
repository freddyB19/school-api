from apps.user.models import User, TypeRole
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

class ChangePermissionAdmin:
	def __init__(self, user: User) -> None:
		self.user = user

		if user.role != TypeRole.admin:
			raise ValueError(f"El usuario debe tener role 'admin' - [id, role]: [{user.id}, {user.role}]")

	def change_permissions(self):
		if not self.user.has_perm("user.can_change_user_role"):
			content_type = ContentType.objects.get_for_model(User)
			permission = Permission.objects.get(
				codename="can_change_user_role",
				content_type=content_type,
			)
			self.user.user_permissions.add(permission)



class ChangePermissionStaff:
	def __init__(self, user: User) -> None:
		self.user = user

		if user.role != TypeRole.staff:
			raise ValueError(f"El usuario debe tener role 'staff' - [id, role]: [{user.id}, {user.role}]")

	def change_permissions(self):
		if self.user.has_perm("user.can_change_user_role"):
			content_type = ContentType.objects.get_for_model(User)
			permission = Permission.objects.get(
				codename="can_change_user_role",
				content_type=content_type,
			)
			self.user.user_permissions.remove(permission)


class ChangeRole:
	@classmethod
	def get(cls, type: int, user: User):

		if type == TypeRole.admin:
			return ChangePermissionAdmin(user = user)
		elif type == TypeRole.staff:
			return ChangePermissionStaff(user = user)
		else:
			return None