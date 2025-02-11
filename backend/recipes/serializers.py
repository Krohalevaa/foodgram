import base64

from rest_framework import serializers
from django.core.files.base import ContentFile
from django.contrib.auth import authenticate, get_user_model
from djoser.serializers import UserCreateSerializer

from .models import (Recipe, Ingredient, Tag, RecipeIngredient,
                     FavoriteRecipe, ShoppingList, Subscription)

User = get_user_model()


class UserLoginSerializer(serializers.Serializer):
    """Сериализатор для входа пользователей"""
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
    """Поле для кодирования изображения в base64."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя"""
    password = serializers.CharField(write_only=True)

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'password')

    def create(self, validated_data):
        """Создание пользователя с хешированным паролем"""
        password = validated_data.pop('password')  # Извлекаем пароль
        user = User(**validated_data)  # Создаем пользователя
        user.set_password(password)  # Устанавливаем хешированный пароль
        user.save()  # Сохраняем пользователя
        return user


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиента"""
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тега"""
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор связи ингредиента и рецепта"""
    ingredient = IngredientSerializer(read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('ingredient', 'amount')

    def get_ingredient(self, obj):
        """Возвращает информацию об ингредиенте."""
        return {
            "id": obj.ingredient.id,
            "name": obj.ingredient.name,
            "unit": obj.ingredient.unit
        }


class RecipeIngredientInputSerializer(serializers.ModelSerializer):
    """Сериализатор для ввода ингредиентов в рецепте"""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(), source='ingredient')
    amount = serializers.FloatField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeIngredientOutputSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода ингредиентов в рецепте"""
    ingredient = IngredientSerializer(read_only=True)
    amount = serializers.FloatField()

    class Meta:
        model = RecipeIngredient
        fields = ('ingredient', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецепта"""
    author = serializers.SerializerMethodField()
    image = Base64ImageField(required=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        write_only=True,
        required=False)
    ingredients = RecipeIngredientInputSerializer(
        many=True,
        source='recipe_ingredients',
        write_only=True,
        required=False)

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'text', 'cooking_time', 'author',
            'tags', 'ingredients', 'image', 'slug', 'creation_date',
            'is_favorited', 'is_in_shopping_cart'
        ]
        extra_kwargs = {"author": {"read_only": True}}

    def to_representation(self, instance):
        """Преобразует модель рецепта в словарь для сериализации."""
        rep = super().to_representation(instance)
        rep['tags'] = TagSerializer(instance.tags.all(), many=True).data
        rep['ingredients'] = [
            {
                'id': ri.ingredient.id,
                'name': ri.ingredient.name,
                'unit': ri.ingredient.unit,
                'amount': ri.amount
            }
            for ri in instance.recipe_ingredients.all()
        ]
        return rep

    def get_author(self, obj):
        """Получает информацию об авторе рецепта."""
        author = obj.author
        return {
            "id": author.id,
            "username": author.username,
            "first_name": author.first_name,
            "last_name": author.last_name,
            'avatar': obj.author.avatar.url if obj.author.avatar else None
        }

    def get_is_favorited(self, obj):
        """Проверяет, добавлен ли рецепт в избранное текущим пользователем."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return FavoriteRecipe.objects.filter(user=request.user, recipe=obj).exists()
        return False

    def create(self, validated_data):
        """Создает новый рецепт на основе валидных данных."""
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
        """Обновляет существующий рецепт на основе валидных данных."""
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

    def get_is_in_shopping_cart(self, obj):
        """Метод для определения, находится ли рецепт в списке покупок текущего пользователя"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ShoppingList.objects.filter(user=request.user, recipe=obj).exists()
        return False


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для избранных рецептов"""
    class Meta:
        model = FavoriteRecipe
        fields = '__all__'


class ShoppingListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок"""
    class Meta:
        model = ShoppingList
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя"""
    avatar = Base64ImageField(required=False, allow_null=True)
    recipes = RecipeSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'avatar', 'recipes', 'is_subscribed')

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий аутентифицированный пользователь на переданный объект."""
        user = self.context.get('request').user
        if user is None:
            return False
        return Subscription.objects.filter(author=obj, subscriber=user).exists() if user.is_authenticated else False

    def update(self, instance, validated_data):
        """Обновляет данные экземпляра модели на основе предоставленных данных."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок пользователей"""
    author = UserSerializer(read_only=True)
    recipes = serializers.SerializerMethodField()
    username = serializers.CharField(source='author.username', read_only=True)
    first_name = serializers.CharField(source='author.first_name', read_only=True)
    last_name = serializers.CharField(source='author.last_name', read_only=True)
    avatar = serializers.ImageField(source='author.avatar', read_only=True)

    class Meta:
        model = Subscription
        fields = '__all__'

    def get_recipes(self, obj):
        """Возвращает список рецептов автора подписки, который передается через контекст."""
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
