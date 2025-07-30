from rest_framework import (
	views, 
	status, 
	response, 
	generics
)

from apps.management.models import Administrator

from . import serializers

class AdministratorAPIView(views.APIView):

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