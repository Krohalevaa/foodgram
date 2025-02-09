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
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    # ingredient = IngredientSerializer(read_only=True)
    ingredient = serializers.SerializerMethodField()

    class Meta:
        model = RecipeIngredient
        fields = ('ingredient', 'quantity')

    def get_ingredient(self, obj):
        # Здесь возвращаем все нужные поля ингредиента
        return {
            "id": obj.ingredient.id,
            "name": obj.ingredient.name,
            "unit": obj.ingredient.unit
        }


class RecipeIngredientInputSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    quantity = serializers.FloatField(min_value=1, required=False, default=1)


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    slug = serializers.SlugField(required=False)
    tags = TagSerializer(required=False, many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(many=True, source='recipe_ingredients', read_only=True)
    image = Base64ImageField(required=True)
    creation_date = serializers.DateField(required=False)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'
        extra_kwargs = {
            "author": {"read_only": True},
        }

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
        tags = validated_data.pop('tags', [])
        ingredients_data = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            RecipeTag.objects.create(recipe=recipe, tag=tag)
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data['id']
            quantity = ingredient_data['quantity']
            ingredient_obj = get_object_or_404(Ingredient, id=ingredient_id)
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient_obj,
                quantity=quantity
            )
        return recipe


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
    

