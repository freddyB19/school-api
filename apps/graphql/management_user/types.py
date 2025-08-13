
from graphene_django import DjangoObjectType

from apps.user.models import User

class UserType(DjangoObjectType):
	class Meta:
		model = User
		fields = ("id", "name", "email", "role")
		convert_choices_to_enum = ["role"]
