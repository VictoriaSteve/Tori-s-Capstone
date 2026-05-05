from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'address',
            'phone_number',
            'password',
            'confirm_password'
        ]

    def validate(self, attrs):
        first_name = attrs.get("first_name")
        last_name = attrs.get("last_name")
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        # prevent crash if empty
        if not first_name or not last_name:
            raise serializers.ValidationError("Name fields are required")

        if first_name[0].islower():
            raise serializers.ValidationError({"first_name": "Must start with capital letter."})

        if last_name[0].islower():
            raise serializers.ValidationError({"last_name": "Must start with capital letter."})

        if password != confirm_password:
            raise serializers.ValidationError({"password": "Passwords do not match."})

        validate_password(password)

        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")

        user = User.objects.create_user(**validated_data)
        return user