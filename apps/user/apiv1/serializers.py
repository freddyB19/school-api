from django.contrib.auth.models import Permission

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.user import models

from apps.user.commands.commands import create_user


REQUIRED_PASSWORD_CONFIRM = "Debe enviar un password de confirmación"
REQUIRED_EMAIL = "Debe enviar un email para el usuario"
REQUIRED_PASSWORD = "Debe enviar un password"
REQUIRED_NAME = "Debe enviar un nombre para el usuario"
MIN_LEN_NAME = "El nombre es muy corto"
MAX_LEN_NAME = "El nombre de usuario es muy largo"
MIN_LEN_PASSWORD = "La contraseña es muy corta"
EMAIL_ALREADY_REGISTERED = "Ya existe un usuario con este email"
PASSWORDS_NOT_MATCH = "Las contraseñas no coinciden"

class UserRegisterSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(
        style={
            "input_type":"password"
        }, 
        write_only = True,
        error_messages = {"required": REQUIRED_PASSWORD_CONFIRM}
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
                        message = EMAIL_ALREADY_REGISTERED
                    )
                ],
                "error_messages": {
                    'required': REQUIRED_EMAIL,
                }
            },
            "password": {
                "min_length": models.MIN_LENGTH_PASSWORD,
                "error_messages": {
                    'required': REQUIRED_PASSWORD,
                    'min_length': MIN_LEN_PASSWORD
                }
            },
            "name": {
                "required": True,
                "max_length": models.MAX_LENGTH_NAME,
                "min_length": models.MIN_LENGTH_NAME,

                "error_messages": {
                    'max_length': MAX_LEN_NAME,
                    'min_length': MIN_LEN_NAME,
                    'required': REQUIRED_NAME,
                }
            }
        }
    
    def validate(self, data):

        password = data.get("password")
        password_confirm = data.get("password_confirm")

        if password != password_confirm:
            raise serializers.ValidationError(PASSWORDS_NOT_MATCH)

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
        min_length = models.MIN_LENGTH_PASSWORD
    )
    password_confirm = serializers.CharField(
        style={
            "input_type":"password"
        },
        min_length = models.MIN_LENGTH_PASSWORD
    )

    def validate(self, data):
        password = data.get("password")
        password_confirm = data.get("password_confirm")

        if password != password_confirm:
            raise serializers.ValidationError(PASSWORDS_NOT_MATCH)

        return data


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        error_messages = {
            "required": REQUIRED_EMAIL
        }
    )
    password = serializers.CharField(
        style={'input_type': 'password'},
        error_messages = {
            "required": REQUIRED_PASSWORD
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