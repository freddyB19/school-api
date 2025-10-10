from django.contrib.auth.models import Permission

from rest_framework import serializers

from apps.user import models


class UserUpdateRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ["role"]

class UserPermissionsSerializer(serializers.Serializer):
    permissions = serializers.ListField(child = serializers.CharField())


    def validate_permissions(self, value):
        if not value:
            raise serializers.ValidationError("Debe indicar que permisos desea agregar al usuario")
        
        exists_permissions = Permission.objects.filter(codename__in = value)

        if not exists_permissions:
            raise serializers.ValidationError("No existe ningún permiso con alguno de esos nombres")
        
        return value


class MUserResposeSerializer(serializers.ModelSerializer):
    user_permissions = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='codename'
    )

    class Meta:
        model = models.User
        fields = [
            "id", 
            "name", 
            "email", 
            "role", 
            "last_login", 
            "date_joined", 
            "is_active",
            "user_permissions"
        ]