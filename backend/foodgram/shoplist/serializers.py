from rest_framework import serializers
from .models import ShopList, Recipe
import base64
from django.core.files.base import ContentFile


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Рецепт. Обрабатывает поля рецепта,
    включая ингредиенты и теги.
    """

    class Meta:
        model = Recipe
        fields = ['id', 'author', 'title', 'image', 'description', 'ingredients', 'tags', 'cooking_time']


class ShopListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Список покупок. Обрабатывает информацию о
    рецептах, добавленных в список покупок.
    """

    class Meta:
        model = ShopList
        fields = ['user', 'recipes']


class Base64ImageField(serializers.ImageField):
    """
    Кастомное поле для обработки изображений в формате base64.
    Позволяет декодировать строку base64 и сохранять её как файл изображения.
    """

    def to_internal_value(self, data):
        """Переводит строку base64 в изображение и сохраняет его как файл."""
        if isinstance(data, str) and data.startswith('data:image'):
            # Извлечение содержимого изображения из строки base64
            format, imgstr = data.split(';base64,')  # Разделяем строку по формату и содержимому
            ext = format.split('/')[1]  # Извлекаем формат изображения (jpeg, png)
            data = ContentFile(base64.b64decode(imgstr), name=f'temp.{ext}')
        return super().to_internal_value(data)
