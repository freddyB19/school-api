from django.dispatch import receiver

from apps.emails.services.reset_password import EmailResetPassword

from .signals import SignalResetPassword, reset_password

subject = "Restableciendo contraseña"
from_email = "freddy@gmail.com"
to = []

@receiver(reset_password, sender=SignalResetPassword)
def reset_password_receiver(sender, **kwargs):
	if "plain_password" in kwargs and "name" in kwargs and "email" in kwargs:

		data_for_email = {
			"user_name": kwargs.get("name"),
			"plain_password": kwargs.get("plain_password"),
			"emails_to": [kwargs.get("email")],
		}

		email = EmailResetPassword(**data_for_email)
		
		#email.send()
