import graphene
from graphene import relay
from graphene_django import DjangoObjectType

from apps.user.models import User
from apps.management.models import Administrator

class UserType(DjangoObjectType):
	userId = graphene.Int()
	role = graphene.Int()
	
	class Meta:
		model = User
		fields = ("id", "name", "email", "date_joined", "last_login")
		interfaces = (relay.Node,)

	def resolve_userId(obj, info):
		return obj.id

	def resolve_role(obj, info):
		return obj.role

class UserConnection(relay.Connection):
	
	class Meta:
		node = UserType

class AdministratorType(DjangoObjectType):
	
	class Meta:
		model = Administrator
		fields = ("id", "school")