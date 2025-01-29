import base64

from rest_framework import serializers
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

from .models import User


User = get_user_model()


class UserLoginSerializer(serializers.Serializer):
    """Сериализатор для авторизации пользователя по email."""
    email = serializers.EmailField()
    password = serializers.CharField()

    # def validate(self, data):
    #     email = data.get("email")
    #     password = data.get("password")
        # user = User.objects.filter(email=email).first()

        # if email and password:
        #     user = authenticate(email=email, password=password)
        #     if user:
        #         # Генерация и возврат токена
        #         token, created = Token.objects.get_or_create(user=user)
        #         return {'token': token.key}
        #     raise AuthenticationFailed('Invalid credentials')
        # raise AuthenticationFailed('Email and password required')


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя. Содержит информацию о пользователе."""
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'email')


class RegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации нового пользователя."""

    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password')

    def create(self, validated_data):
        """Создание нового пользователя с хэшированием пароля."""
        user = User.objects.create_user(**validated_data)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Сериализатор для смены пароля."""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value


class UserAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для фото пользователя с поддержкой base64 изображения."""
    avatar = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('avatar',)

    def to_internal_value(self, data):
        """Метод для преобразования base64 строки в изображение."""
        avatar_data = data.get('avatar')
        if avatar_data:
            format, imgstr = avatar_data.split(';base64,')
            ext = format.split('/')[-1]
            avatar = ContentFile(base64.b64decode(imgstr),
                                 name='avatar.' + ext)
            data['avatar'] = avatar
        return data


class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = ('id', 'email', 'username', 'password')
