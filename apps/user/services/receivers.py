from django.dispatch import receiver

from apps.emails.services.reset_password import EmailResetPassword

from .signals import SignalResetPassword, reset_password

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
