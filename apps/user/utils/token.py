from typing import Dict

from rest_framework_simplejwt.tokens import RefreshToken

from apps.user.models import User


class Token:

	@classmethod
	def get(cls, user: User):
		token = RefreshToken.for_user(user)

		return {
			"access": str(token),
			"refresh": str(token.access_token)
		}
