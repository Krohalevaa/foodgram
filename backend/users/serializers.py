import base64

from rest_framework import serializers
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя. Содержит информацию о пользователе."""
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'email')


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
