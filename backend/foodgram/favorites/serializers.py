from rest_framework import serializers
from .models import Favorite, Recipe, User
import base64
from django.core.files.base import ContentFile
from io import BytesIO

# Сериализатор для модели Favorite
class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['user', 'recipe', 'created_at']

    # Добавление кастомной логики для сериализации картинки
    def to_internal_value(self, data):
        # Проверка на base64 строку
        if 'image' in data:
            image_data = base64.b64decode(data['image'])
            file_name = 'image.png'
            data['image'] = ContentFile(image_data, name=file_name)
        return super().to_internal_value(data)

# Сериализатор для работы с изображениями
class RecipeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['title', 'image']

    def to_internal_value(self, data):
        if 'image' in data:
            image_data = base64.b64decode(data['image'])
            file_name = 'recipe_image.png'
            data['image'] = ContentFile(image_data, name=file_name)
        return super().to_internal_value(data)
