from django.contrib.auth.models import Permission

from rest_framework import (
	views, 
	status, 
	response, 
	generics
)
from rest_framework.permissions import IsAuthenticated


from apps.user.commands.commands import get_user
from apps.user.apiv1.serializers import (
	UserResposeSerializer, 
	UserPermissionsSerializer
)
from apps.user.apiv1.permissions import IsRoleAdminOrReadOnly

from apps.utils.result_commands import (
    ResponseError,
    ResponseSuccess
)


from . import serializers
from apps.management.models import Administrator


class AdministratorAPIView(views.APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request, school_id: int = None):
		try:
		
			admin = Administrator.objects.defer("school").prefetch_related(
				"users"
			).get(school_id = school_id)
		
		except Administrator.DoesNotExist as e:
			return response.Response(
				data = {
					"error": {"message": f"No existe información sobre los administradores del portal de un colegio con ID: {school_id}"}
				},
				status = status.HTTP_404_NOT_FOUND
			)

		serializer = serializers.AdministratorResponse(admin)

		return response.Response(
			data = serializer.data,
			status = status.HTTP_200_OK
		)

class AdministratorDetailAPIView(generics.RetrieveAPIView):
	queryset = Administrator.objects.all()
	serializer_class = serializers.AdministratorDetailResponse
	permission_classes = [IsAuthenticated]
	
	def get_object(self):
		try:
			return self.queryset.prefetch_related(
				"users"
			).get(pk = self.kwargs.get("pk"))
		except Administrator.DoesNotExist as e:
			return None
	
	def retrieve(self, request, *args, **kwargs):
		admin = self.get_object()

		if not admin:
			return response.Response(
				data = {
					"error": {"message": f"No existe información sobre los administradores de este portal con ID: {kwargs.get('pk')}"}
				},
				status = status.HTTP_404_NOT_FOUND
			)

		serializer = self.get_serializer(admin)

		return response.Response(
			data = serializer.data,
			status = status.HTTP_200_OK
		)


class UpdatePermissionsUser(views.APIView):
	permission_classes = [IsAuthenticated, IsRoleAdminOrReadOnly]

	def patch(self, request, pk):

		command = get_user(pk = pk)

		if not command.status:
			return response.Response(
				data = ResponseError(
					errors = command.errors
				).model_dump(),
				status = status.HTTP_404_NOT_FOUND
			)

		serializer = UserPermissionsSerializer(data = request.data)

		if not serializer.is_valid():
			return response.Response(
				data = serializer.errors,
				status = status.HTTP_400_BAD_REQUEST
			)

		user = command.query

		permissions = Permission.objects.filter(
			codename__in = serializer.data['permissions']
		)

		user.user_permissions.set(permissions)

		return response.Response(
			data = UserResposeSerializer(user).data,
			status = status.HTTP_200_OK
		) 