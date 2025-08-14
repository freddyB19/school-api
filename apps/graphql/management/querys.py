import graphene
from graphene import relay
from apps.management.models import Administrator

from .types import (
	UserConnection,
	AdministratorType
)

AdministratorDoesNotExist = None

class AdministratorDetailQuery(graphene.ObjectType):
	detail = graphene.Field(
		AdministratorType, 
		pk = graphene.Int(required = True)
	)
	admins = relay.ConnectionField(
		UserConnection, 
		pk = graphene.Int(required = True)
	)

	def resolve_detail(root, info, pk):
		try:
			administrator = Administrator.objects.select_related(
				"school"
			).get(id = pk)
		except Administrator.DoesNotExist as e:
			return AdministratorDoesNotExist
		
		return administrator


	def resolve_admins(root, info, pk, **kwargs):
		try:
			administrator = Administrator.objects.prefetch_related(
				"users"
			).get(id = pk)
		except Administrator.DoesNotExist as e:
			return Administrator.objects.none()

		return administrator.users.all()
