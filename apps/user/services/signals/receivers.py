from django.dispatch import receiver

from apps.emails.services.reset_password import EmailResetPassword

from .signals import (
	SignalResetPassword, 
	reset_password,
	SignalChangeRole,
	change_role
)
from .utils.class_receivers import ChangeRole


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


@receiver(change_role, sender = SignalChangeRole)
def change_role_receiver(sender, **kwargs):
	if "role" in kwargs and "user" in kwargs:
		
		role = ChangeRole.get(
			type = kwargs.get("role"), 
			user = kwargs.get("user")
		)

		if role:
			role.change_permissions()
