from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission

from apps.emails.services.reset_password import EmailResetPassword
from apps.user.model import User, TypeRole

from .signals import (
	SignalResetPassword, 
	reset_password,
	SignalChangeRole,
	change_role
)


subject = "Restableciendo contraseña"
from_email = "freddy@gmail.com"
to = []

@receiver(reset_password, sender=SignalResetPassword)
def reset_password_receiver(sender, **kwargs):
	if "plain_password" in kwargs and "name" in kwargs and "email" in kwargs:

		email = EmailResetPassword(
			data_message = {
				"name_user": kwargs.get("name"),
				"password": kwargs.get("plain_password")
			},
			emails_to = [kwargs.get("email")]
		)
		
		email.send()


class ChangePermissionAdmin:
	def __init__(self, user: User) -> None:
		self.user = user

		if user.role != TypeRole.admin:
			raise ValueError(f"El usuario debe tener role 'admin' - [id, role]: [{user.id}, {user.role}]")

	def change_permissions(self):
		if not user.has_perm("user.can_change_user_role"):
			content_type = ContentType.objects.get_for_model(User)
			permission = Permission.objects.get(
				codename="can_change_user_role",
				content_type=content_type,
			)
			user.user_permissions.add(permission)


class ChangePermissionStaff:
	def __init__(self, user: User) -> None:
		self.user = user

		if user.role != TypeRole.staff:
			raise ValueError(f"El usuario debe tener role 'staff' - [id, role]: [{user.id}, {user.role}]")

	def change_permissions(self):
		if user.has_perm("user.can_change_user_role"):
			content_type = ContentType.objects.get_for_model(User)
			permission = Permission.objects.get(
				codename="can_change_user_role",
				content_type=content_type,
			)
			user.user_permissions.remove(permission)


class ChangeRole:
	def get(cls, type: int, user: User):

		if type == TypeRole.admin:
			# add permiso
			return ChangePermissionAdmin(user = user)
		elif type == TypeRole.staff:
			# validar que lo tiene
			# remover permiso
			return ChangePermissionStaff(user = user)
		else:
			# None
			return None


@receiver(change_role, sender = SignalChangeRole)
def change_role_to_admin(sender, **kwargs):
	if "role" in kwargs and "user" in kwargs:
		
		role = ChangeRole(type = kwargs["role"], user = kwargs["user"])

		if role:
			role.change_permissions()
