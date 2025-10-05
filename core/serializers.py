from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email', 'role',
            'is_active', 'password', 'is_staff', 'is_superuser', 'date_joined', 'last_login'
        ]
        read_only_fields = ['is_staff', 'is_superuser', 'date_joined', 'last_login']

    def validate_password(self, value):
        if value is None or value == '':
            return value
        if len(value) < 8:
            raise serializers.ValidationError('Password must be at least 8 characters long')
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            # Set unusable if not provided
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


