from rest_framework import serializers
from django.core.files.base import ContentFile
import base64

from .models import Recipe, Tag, Ingredient


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Тег"""
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ингредиент"""
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'unit']


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Рецепт"""
    ingredients = IngredientSerializer(many=True)
    tags = TagSerializer(many=True)
    image = serializers.ImageField(write_only=True)

    class Meta:
        model = Recipe
        fields = ['id',
                  'title',
                  'author',
                  'description',
                  'ingredients',
                  'tags',
                  'cooking_time',
                  'image']

    def create(self, validated_data):
        """Кастомная логика для создания рецепта"""
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.create(**ingredient_data)
            recipe.ingredients.add(ingredient)

        for tag_data in tags_data:
            tag = Tag.objects.create(**tag_data)
            recipe.tags.add(tag)

        return recipe

    def to_internal_value(self, data):
        """Кастомная обработка изображения base64"""
        image_data = data.get('image', None)
        if image_data:
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            img_data = base64.b64decode(imgstr)
            file_name = 'recipe_image.' + ext
            file = ContentFile(img_data, file_name)
            data['image'] = file
        return super().to_internal_value(data)
