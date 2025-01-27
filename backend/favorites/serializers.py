import base64

from rest_framework import serializers
from django.core.files.base import ContentFile

from .models import FavoriteRecipe


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Favorite"""
    class Meta:
        model = FavoriteRecipe
        fields = ['user', 'recipe', 'created_at']

    def to_internal_value(self, data):
        """Добавление кастомной логики для сериализации картинки"""
        if 'image' in data:
            image_data = base64.b64decode(data['image'])
            file_name = 'image.png'
            data['image'] = ContentFile(image_data, name=file_name)
        return super().to_internal_value(data)


class RecipeImageSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с изображениями"""
    class Meta:
        model = FavoriteRecipe
        fields = ['title', 'image']

    def to_internal_value(self, data):
        if 'image' in data:
            image_data = base64.b64decode(data['image'])
            file_name = 'recipe_image.png'
            data['image'] = ContentFile(image_data, name=file_name)
        return super().to_internal_value(data)
