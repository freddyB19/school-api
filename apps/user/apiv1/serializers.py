from django.contrib.auth.models import Permission

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.user import models
from apps.user.models import (
    MAX_LENGTH_NAME,
    MIN_LENGTH_NAME,
    MIN_LENGTH_PASSWORD
)


from apps.user.commands.commands import is_valid_email, create_user

class UserRegisterSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(
        style={
            "input_type":"password"
        }, 
        write_only = True,
        error_messages = {"required": "Debe enviar un password de confirmación"}
    )
    
    class Meta:
        model = models.User
        fields = [
            "name",
            "email",
            "password",
            "password_confirm",
        ]
        extra_kwargs = {
            "email":{
                "validators": [
                    UniqueValidator(
                        queryset = models.User.objects.all(),
                        message = "Ya existe un usuario con este email"
                    )
                ],
                "error_messages": {
                    'required': "Debe enviar un email para el usuario",
                }
            },
            "password": {
                "error_messages": {
                    'required': "Debe enviar un password",
                }
            },
            "name": {
                "required": True,
                "max_length": MAX_LENGTH_NAME,
                "error_messages": {
                    'max_length': "El nombre de usuario es muy largo",
                    'required': "Debe enviar un nombre para el usuario",
                }
            }
        }
    
    def validate_name(self, value):

        if len(value) < MIN_LENGTH_NAME:
            raise serializers.ValidationError("El nombre es muy corto")

        return value

    def validate_password(self, value):
        
        if len(value) < MIN_LENGTH_PASSWORD:
            raise serializers.ValidationError("La contraseña es muy corta")
        
        return value

    def validate(self, data):

        password = data.get("password")
        password_confirm = data.get("password_confirm")

        if password != password_confirm:
            raise serializers.ValidationError("Las contraseñas no coinciden")

        return data

    def create(self, validate_data):

        command = create_user(user = validate_data)

        if not command.status:
            raise serializers.ValidationError(ResponseError(
                errors = command.errors
            ).model_dump())

        return command.query


class UserUpdateRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ["role"]


class UserResposeSerializer(serializers.ModelSerializer):
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

class UserChangePassword(serializers.Serializer):
    password = serializers.CharField(
        style={
            "input_type":"password"
        }, 
        min_length = MIN_LENGTH_PASSWORD
    )
    password_confirm = serializers.CharField(
        style={
            "input_type":"password"
        },
        min_length = MIN_LENGTH_PASSWORD
    )

    def validate(self, data):
        password = data.get("password")
        password_confirm = data.get("password_confirm")

        if password != password_confirm:
            raise serializers.ValidationError("Las contraseñas no coinciden")

        return data




class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        error_messages = {
            "required": "Debe enviar un email"
        }
    )
    password = serializers.CharField(
        style={'input_type': 'password'},
        error_messages = {
            "required": "Debe enviar un password"
        }
    )

class TokenSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class UserResponseLogin(serializers.Serializer):
    user = UserResposeSerializer(read_only = True)
    token = TokenSerializer()


class UserPermissionsSerializer(serializers.Serializer):
    permissions = serializers.ListField(child = serializers.CharField())


    def validate_permissions(self, value):
        if not value:
            raise serializers.ValidationError("Debe indicar que permisos desea agregar al usuario")
        
        exists_permissions = Permission.objects.filter(codename__in = value)

        if not exists_permissions:
            raise serializers.ValidationError("No existe ningún permiso con alguno de esos nombres")
        
        return value