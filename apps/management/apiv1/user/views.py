
from django.contrib.auth.models import Permission

from rest_framework import (
    views, 
    status, 
    response, 
    generics
)
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema

from apps.utils.result_commands import ResponseError

from apps.user import models
from apps.user.commands.commands import get_user

from apps.user.apiv1.permissions import (
	IsRoleAdminOrReadOnly,
	AdminCannotChangeOwnRole
)

from apps.user.apiv1.serializers import (
	UserResposeSerializer, 
	UserUpdateRoleSerializer,
	UserPermissionsSerializer,
)


class UpdateUserPermissions(generics.UpdateAPIView):
	queryset = models.User.objects.all()
	serializer_class = UserResposeSerializer
	permission_classes = [IsAuthenticated, IsRoleAdminOrReadOnly]


	def update(self, request, pk, **kwargs):
		user = self.get_object()
		serializer = UserPermissionsSerializer(data = request.data)

		if not serializer.is_valid():
			return response.Response(
				data = serializer.errors,
				status = status.HTTP_400_BAD_REQUEST
			)

		permissions = Permission.objects.filter(
			codename__in = serializer.data['permissions']
		)

		user.user_permissions.set(permissions)

		return response.Response(
			data = self.get_serializer(user).data,
			status = status.HTTP_200_OK
		)


class UpdateUserRoleAPIView(generics.UpdateAPIView):
    queryset = models.User.objects.all()
    serializer_class = UserResposeSerializer
    permission_classes = [IsAuthenticated, AdminCannotChangeOwnRole]

    def update(self, request, pk, **kwargs):
        user = self.get_object()

        validate_role = UserUpdateRoleSerializer(data = request.data)

        if not validate_role.is_valid():
            return response.Response(
                data = validate_role.errors,
                status = status.HTTP_400_BAD_REQUEST
            )

        user.role = validate_role.data['role']
        user.save()

        return response.Response(
            data = UserResposeSerializer(user).data,
            status = status.HTTP_200_OK
        )