from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from .models import CustomUser

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'confirm']

    def validate(self, data):
        if data['password'] != data['confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm')
        user = CustomUser.objects.create_user(
            username=validated_data['username'],  # 👈 use name as username
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


