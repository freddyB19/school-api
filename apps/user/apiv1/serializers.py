
from rest_framework import serializers

from apps.utils.result_commands import ResponseError

from apps.user import models

from apps.user.commands.commands import change_password


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

    def update(self, instance, validated_data) -> models.User:
        command = change_password(
            pk = self.context.get("pk"),
            new_password = validated_data.get('password')
        )

        if not command.status:
            raise serializers.ValidationError(
                ResponseError(
                    errors = command.errors
                ).model_dump(exclude_defaults = True),
                code="does-not-exist"
            )

        return instance
