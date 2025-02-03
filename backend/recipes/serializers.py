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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'password')
    
    def validate(self, attrs):
        if not attrs.get('username'):
            raise serializers.ValidationError({"username": "Это поле обязательно."})
        return attrs


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
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault())

    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(many=True, source='ingredient_for_recipe', read_only=True)
    image = Base64ImageField(required=True)
    creation_date = serializers.DateField(required=False)

    class Meta:
        model = Recipe
        fields = '__all__'
        # fields = ('id', 'name', 'description', 'image', 'preparation_time', 'author', 'tags', 'ingredients', 'slug', 'creation_date')
    
    

class FavoriteRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteRecipe
        fields = '__all__'


class ShoppingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingList
        fields = '__all__'


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'

