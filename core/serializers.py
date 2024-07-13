from typing import Any

from rest_framework import serializers

from core.models import User


class UserSerializer(serializers.HyperlinkedModelSerializer):  # type: ignore[type-arg]
    class Meta:
        model = User
        fields = (
            "id",
            "name",
            "email",
            "password",
            "is_active",
            "is_staff",
            "is_superuser",
            "last_login",
            "created_at",
            "updated_at",
            "url",
        )
        read_only_fields = ("is_active", "is_staff", "is_superuser", "last_login")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data: dict[str, Any]) -> User:
        """Password is hashed before saving to the database"""
        password = validated_data.pop("password", None)

        instance: User = super().create(validated_data)

        # set_password() hashes the password before saving to the database
        instance.set_password(password)
        instance.save()

        return instance

    def update(self, instance: User, validated_data: dict[str, Any]) -> User:
        """Password is hashed before saving to the database"""
        password = validated_data.pop("password", None)

        instance = super().update(instance, validated_data)

        if password:
            # set_password() hashes the password before saving to the database
            instance.set_password(password)
            instance.save()

        return instance
