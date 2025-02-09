import base64

from rest_framework import serializers
from django.core.files.base import ContentFile
from django.contrib.auth import authenticate, get_user_model
from djoser.serializers import UserCreateSerializer
from .models import Recipe, Ingredient, Tag, RecipeIngredient, FavoriteRecipe, ShoppingList, Subscription, RecipeTag
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404

User = get_user_model()


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data['email']
        password = data['password']
        user = authenticate(email=email, password=password)
        if user is None:
            raise serializers.ValidationError("Invalid credentials")
        return user


class Base64ImageField(serializers.ImageField):
    """Кастомное поле для кодирования изображения в base64."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'password')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']
        # fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('ingredient', 'amount')

    def get_ingredient(self, obj):
        return {
            "id": obj.ingredient.id,
            "name": obj.ingredient.name,
            "unit": obj.ingredient.unit
        }


class RecipeIngredientInputSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(), source='ingredient')
    amount = serializers.FloatField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeIngredientOutputSerializer(serializers.ModelSerializer):
    # id = serializers.ReadOnlyField(source='ingredient.id')
    # name = serializers.ReadOnlyField(source='ingredient.name')
    # unit = serializers.ReadOnlyField(source='ingredient.unit')
    ingredient = IngredientSerializer(read_only=True) 
    amount = serializers.FloatField()

    class Meta:
        model = RecipeIngredient
        fields = ('ingredient', 'amount')
        # fields = ('id', 'name', 'unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    image = Base64ImageField(required=True)
    is_favorited = serializers.SerializerMethodField()

    # tags = TagSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, write_only=True)
    # displayed_tags = TagSerializer(
    #     many=True,
    #     source='tags',
    #     read_only=True  # Только для чтения
    # )
    
    
    ingredients = RecipeIngredientInputSerializer(
        many=True,
        source='recipe_ingredients',
        read_only=True
        # write_only=True
    )
    # output_ingredients = RecipeIngredientOutputSerializer(
    #     many=True,
    #     source='recipe_ingredients',
    #     read_only=True
    # ) это нах
    # output_ingredients = RecipeIngredientSerializer(
    #     many=True,
    #     source='recipe_ingredients',
    #     read_only=True
    # )
    tags_info = TagSerializer(
        many=True,
        source='tags',
        read_only=True
    )

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'text', 'cooking_time', 'author',
            'tags', 'tags_info', 'ingredients', 'image', 
            'slug', 'creation_date', 'is_favorited'
        ]
        # fields = '__all__'
        extra_kwargs = {
            "author": {"read_only": True},
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
    # Преобразуем ингредиенты для фронтенда
        data['ingredients'] = [
            {
                'name': i.ingredient.name,
                'unit': i.ingredient.unit,
                'amount': i.amount
            } for i in instance.recipe_ingredients.all()
        ]
        return data

    def get_author(self, obj):
        author = obj.author
        return {
            "id": author.id,
            "username": author.username,
            "first_name": author.first_name,
            "last_name": author.last_name,
            'avatar': obj.author.avatar.url if obj.author.avatar else None
        }
    
    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return FavoriteRecipe.objects.filter(user=request.user, recipe=obj).exists()
        return False
    
    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients', [])
        tags = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=item['ingredient'],
                amount=item['amount']
            ) for item in ingredients_data]
        RecipeIngredient.objects.bulk_create(ingredients)
        return recipe
    
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients', [])
        tags = validated_data.pop('tags', [])
        instance = super().update(instance, validated_data)
        instance.tags.set(tags)
        instance.recipe_ingredients.all().delete()
        ingredients = [
            RecipeIngredient(
                recipe=instance,
                ingredient=item['ingredient'],
                amount=item['amount']
            ) for item in ingredients_data]
        RecipeIngredient.objects.bulk_create(ingredients)
        return instance


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteRecipe
        fields = '__all__'


class ShoppingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingList
        fields = '__all__'



class UserSerializer(serializers.ModelSerializer):

    avatar = Base64ImageField(required=False, allow_null=True)
    recipes = RecipeSerializer(many=True, read_only=True)  # Рецепты пользователя
    is_subscribed = serializers.SerializerMethodField() 
 
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'avatar', 'recipes', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return Subscription.objects.filter(author=obj, subscriber=user).exists() if user.is_authenticated else False
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class SubscriptionSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    recipes = serializers.SerializerMethodField()
    username = serializers.CharField(source='author.username', read_only=True)
    first_name = serializers.CharField(source='author.first_name', read_only=True)
    last_name = serializers.CharField(source='author.last_name', read_only=True)
    avatar = serializers.ImageField(source='author.avatar', read_only=True)  # Поле для аватара пользователя
    # recipes = RecipeSerializer(many=True, read_only=True)
    
    class Meta:
        model = Subscription
        fields = '__all__'
    
    def get_recipes(self, obj):
        """
        Возвращает список рецептов автора подписки, ограниченный по параметру recipes_limit,
        который передается через контекст.
        """
        recipes_limit = self.context.get('recipes_limit')
        recipes_qs = obj.author.recipes.all()
        if recipes_limit:
            try:
                recipes_limit = int(recipes_limit)
                recipes_qs = recipes_qs[:recipes_limit]
            except ValueError:
                pass
        serializer = RecipeSerializer(recipes_qs, many=True, context=self.context)
        return serializer.data
    

