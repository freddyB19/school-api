
from django.contrib.auth.models import Permission

from rest_framework import (
    views, 
    status, 
    response, 
    generics
)
from rest_framework.permissions import IsAuthenticated

from apps.user import models

from apps.user.apiv1.permissions import (
	IsRoleAdminOrReadOnly,
	AdminCannotChangeOwnRole
)

from . import serializers


class UpdateUserPermissions(generics.UpdateAPIView):
	queryset = models.User.objects.all()
	serializer_class = serializers.MUserResposeSerializer
	permission_classes = [IsAuthenticated, IsRoleAdminOrReadOnly]


	def update(self, request, pk, **kwargs):
		user = self.get_object()
		serializer = serializers.UserPermissionsSerializer(data = request.data)

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
    serializer_class = serializers.MUserResposeSerializer
    permission_classes = [IsAuthenticated, AdminCannotChangeOwnRole]

    def update(self, request, pk, **kwargs):
        user = self.get_object()

        validate_role = serializers.UserUpdateRoleSerializer(data = request.data)

        if not validate_role.is_valid():
            return response.Response(
                data = validate_role.errors,
                status = status.HTTP_400_BAD_REQUEST
            )

        user.role = validate_role.data['role']
        user.save()

        return response.Response(
            data = self.get_serializer(user).data,
            status = status.HTTP_200_OK
        )