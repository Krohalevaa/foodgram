import base64

from rest_framework import serializers
from django.core.files.base import ContentFile
from django.contrib.auth import authenticate, get_user_model
from djoser.serializers import UserCreateSerializer
from .models import Recipe, Ingredient, Tag, RecipeIngredient, FavoriteRecipe, ShoppingList, Subscription
from rest_framework.response import Response
from django.utils import timezone


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
    ingredient = IngredientSerializer()

    class Meta:
        model = RecipeIngredient
        fields = ('ingredient', 'quantity')
    
    # @api_view(['POST'])
    # def add_ingredient_to_recipe(request):
    #     ingredient_id = request.data.get('ingredient')
    #     if not ingredient_id:
    #         return Response({"error": "Ингредиент не выбран"}, status=status.HTTP_400_BAD_REQUEST)
    
    #     try:
    #         ingredient = Ingredient.objects.get(id=ingredient_id)
    #     except Ingredient.DoesNotExist:
    #         return Response({"error": "Ингредиент не найден"}, status=status.HTTP_404_NOT_FOUND)


class RecipeSerializer(serializers.ModelSerializer):
    # author = UserSerializer(read_only=True)
    author = serializers.SerializerMethodField()
    # author = serializers.PrimaryKeyRelatedField(
    #     queryset=User.objects.all(),
    #     default=serializers.CurrentUserDefault()
    #     )
    # author = UserSerializer(read_only=True)

    slug = serializers.SlugField(required=False)
    tags = TagSerializer(required=False, many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(many=True, source='ingredient_for_recipe', read_only=True)
    image = Base64ImageField(required=True)
    creation_date = serializers.DateField(required=False)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        # fields = ('id', 'name', 'image', 'cooking_time', 'is_favorite')

        fields = '__all__'
        extra_kwargs = {
            "author": {"read_only": True},  # ← Запрещаем передавать author вручную
        }

    
    
    def get_author(self, obj):
        # Получаем автора через поле автор (например, user)
        author = obj.author
        return {
            "id": author.id,
            "username": author.username,
            "first_name": author.first_name,
            "last_name": author.last_name,
            'avatar': obj.author.avatar.url if obj.author.avatar else None
            # Можно добавить другие поля, например, avatar
        }
    
    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return FavoriteRecipe.objects.filter(user=request.user, recipe=obj).exists()
        return False
    


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

        # fields = ('id', 'email', 'username', 'first_name', 'last_name', 'password', 'avatar')
    
    # def validate(self, attrs):
    #     if not attrs.get('username'):
    #         raise serializers.ValidationError({"username": "Это поле обязательно."})
    #     return attrs

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return Subscription.objects.filter(author=obj, subscriber=user).exists() if user.is_authenticated else False
    
    def update(self, instance, validated_data):
        # Обновляем только переданные поля
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
        # Получаем рецепты автора (предполагается, что у модели User есть related_name='recipes' для рецептов)
        recipes_qs = obj.author.recipes.all()
        if recipes_limit:
            try:
                recipes_limit = int(recipes_limit)
                recipes_qs = recipes_qs[:recipes_limit]
            except ValueError:
                pass  # Если переданное значение не число, игнорируем ограничение
        # Сериализуем рецепты (используем ваш RecipeSerializer)
        serializer = RecipeSerializer(recipes_qs, many=True, context=self.context)
        return serializer.data