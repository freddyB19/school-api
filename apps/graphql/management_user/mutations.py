import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError

from apps.school.models import School
from apps.management.models import Administrator
from apps.user.models import User
from apps.user.apiv1.serializers import UserRegisterSerializer
from apps.user.commands.commands import create_user


class UserType(DjangoObjectType):
	class Meta:
		model = User
		fields = ("id", "name", "email", "role")
		convert_choices_to_enum = ["role"]

class UserInput(graphene.InputObjectType):
	name = graphene.String(required = True)
	email = graphene.String(required = True)
	password = graphene.String(required = True)
	password_confirm = graphene.String(required = True)


class AdministratorUserMutation(graphene.Mutation):

	class Arguments:
		user = UserInput(required = True)
		school_id = graphene.Int(required = True)

	user = graphene.Field(UserType)

	def mutate(root, info, user, school_id):

		try:
			school = School.objects.get(pk = school_id)
		except School.DoesNotExist as e:
			raise GraphQLError("No existe una escuela con ese ID")

		admin = Administrator.objects.get(school_id = school.id)

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