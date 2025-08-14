import graphene
from graphql import GraphQLError

from apps.school.models import School
from apps.management.models import Administrator

from apps.user.apiv1.serializers import UserRegisterSerializer

from .types import UserType


class UserInput(graphene.InputObjectType):
	name = graphene.String(required = True)
	email = graphene.String(required = True)
	password = graphene.String(required = True)
	password_confirm = graphene.String(required = True)

AdministratorDoesNotExist = None

class AdministratorUserMutation(graphene.Mutation):

	class Arguments:
		user = UserInput(required = True)
		school_id = graphene.Int(required = True)

	user = graphene.Field(UserType)

	def mutate(root, info, user, school_id):

		try:
			admin = Administrator.objects.get(school_id = school_id)
		except Administrator.DoesNotExist as e:
			return AdministratorDoesNotExist


		serializer_register = UserRegisterSerializer(
			data = {
				"name": user.name, 
				"email":  user.email,
				"password": user.password,
				"password_confirm": user.password_confirm
			}
		)
		
		if not serializer_register.is_valid():
			raise GraphQLError(
				"Error en los datos enviados",
				extensions = {"invalidArguments": serializer_register.errors}
			)

		new_user = serializer_register.save()

		admin.users.add(new_user)
		
		return AdministratorUserMutation(user = new_user)


class ManagementUserMutation(graphene.ObjectType):
	create_user = AdministratorUserMutation.Field()