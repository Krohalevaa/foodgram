import base64

from rest_framework import serializers
from django.core.files.base import ContentFile
from django.contrib.auth import authenticate, get_user_model
from djoser.serializers import UserCreateSerializer
from .models import Recipe, Ingredient, Tag, RecipeIngredient, FavoriteRecipe, ShoppingList, Subscription

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


# class UserLoginSerializer(serializers.Serializer):
    # username = serializers.CharField()
    # email = serializers.EmailField()
    # password = serializers.CharField()

    # def validate(self, data):
    #     email = data['email']
    #     password = data['password']
    #     user = authenticate(email=email, password=password)
    #     if user is None:
    #         raise serializers.ValidationError("Invalid credentials")
    #     return user


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


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(many=True, source='ingredient_for_recipe', read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'description', 'image', 'preparation_time', 'author', 'tags', 'ingredients', 'slug', 'creation_date')


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








# class UserSerializer(serializers.ModelSerializer):
#     """Сериализатор для пользователя. Содержит информацию о пользователе."""
#     subscriber = serializers.SerializerMethodField()

#     class Meta:
#         model = User
#         fields = ('id', 'first_name', 'last_name', 'username', 'email', 'subscriber')


# class UserCreateSerializer(UserCreateSerializer):
#     """Сериализатор для создания пользователя."""
#     class Meta():
#         model = User
#         fields = ('id', 'first_name', 'last_name', 'username', 'email')


# class TagSerializer(serializers.ModelSerializer):
#     """Сериализатор для модели Тег"""
#     class Meta:
#         model = Tag
#         fields = ['id', 'name', 'slug']


# class IngredientSerializer(serializers.ModelSerializer):
#     """Сериализатор для модели Ингредиент"""
#     class Meta:
#         model = Ingredient
#         fields = ['id', 'name', 'unit']


# # NEED TO CORRECT

# class RecipeIngredientSerializer(serializers.ModelSerializer):
#     """Сериализатор для модели ингредиентов в рецепте."""
#     id = serializers.ReadOnlyField(source='ingredient.id')
#     name = serializers.ReadOnlyField(source='ingredient.name')
#     unit = serializers.ReadOnlyField(source='ingredient.unit')

#     class Meta:
#         model = RecipeIngredient
#         fields = ('id', 'name', 'unit', 'quantity')


# class RecipeSerializer(serializers.ModelSerializer):
#     """
#     Сериализатор для модели Рецепт. Обрабатывает поля рецепта,
#     включая ингредиенты и теги.
#     """
#     tags = TagSerializer(many=True)
#     author = UserSerializer()
#     ingredients = RecipeIngredientSerializer(
#         source='ingredient_for_recipe', many=True)
#     favorite_recipes = serializers.SerializerMethodField()
#     shoppinglist_recipe = serializers.SerializerMethodField()

#     class Meta:
#         model = Recipe
#         fields = ['id',
#                   'title',
#                   'description',
#                   'image',
#                   'preparation_time',
#                   'author',
#                   'tags',
#                   'ingredients',
#                   'slug',
#                   'creation_date',
#                   'favorite_recipes',
#                   'ingredient_for_recipe',
#                   'shoppinglist_recipe'
#                   ]


# class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
#     """Сериализатор для ингредиентов в рецептах"""
#     id = serializers.IntegerField()
#     quantity = serializers.IntegerField()

#     @staticmethod
#     def validate_amount(value):
#         """Метод валидации количества"""
#         if value < 1:
#             raise serializers.ValidationError(
#                 'Количество ингредиентов должно быть положительным')
#         return value

#     class Meta:
#         model = RecipeIngredient
#         fields = ('id', 'quantity')


# class CreateRecipeSerializer(serializers.ModelSerializer):
#     """Сериализатор для создания рецептов"""
#     ingredients = RecipeIngredientCreateSerializer(many=True)
#     tags = serializers.PrimaryKeyRelatedField(
#         many=True, queryset=Tag.objects.all())
#     image = Base64ImageField(use_url=True)

#     class Meta:
#         """Мета-параметры сериализатора"""

#         model = Recipe
#         fields = ('ingredients', 'tags', 'name',
#                   'image', 'description', 'preparation_time')

#     def to_representation(self, instance):
#         """Метод представления модели"""

#         serializer = RecipeSerializer(
#             instance,
#             context={
#                 'request': self.context.get('request')
#             }
#         )

#         return serializer.data

#     def validate(self, data):
#         """Метод валидации ингредиентов"""

#         ingredients = self.initial_data.get('ingredients')
#         lst_ingredient = []

#         for ingredient in ingredients:
#             if ingredient['id'] in lst_ingredient:
#                 raise serializers.ValidationError(
#                     'Ингредиенты должны быть уникальными!'
#                 )
#             lst_ingredient.append(ingredient['id'])

#         return data

#     def create_ingredients(self, ingredients, recipe):
#         """Метод создания ингредиента"""

#         for element in ingredients:
#             id = element['id']
#             ingredient = Ingredient.objects.get(pk=id)
#             amount = element['amount']
#             RecipeIngredient.objects.create(
#                 ingredient=ingredient, recipe=recipe, amount=amount
#             )

#     def create_tags(self, tags, recipe):
#         """Метод добавления тега"""

#         recipe.tags.set(tags)

#     def create(self, validated_data):
#         """Метод создания модели"""
#         ingredients = validated_data.pop('ingredients')
#         tags = validated_data.pop('tags')

#         user = self.context.get('request').user
#         recipe = Recipe.objects.create(**validated_data, author=user)
#         self.create_ingredients(ingredients, recipe)
#         self.create_tags(tags, recipe)
#         return recipe

#     def update(self, instance, validated_data):
#         """Метод обновления модели"""

#         RecipeIngredient.objects.filter(recipe=instance).delete()
#         RecipeTag.objects.filter(recipe=instance).delete()

#         self.create_ingredients(validated_data.pop('ingredients'), instance)
#         self.create_tags(validated_data.pop('tags'), instance)

#         return super().update(instance, validated_data)


# class ShopListSerializer(serializers.ModelSerializer):
#     """
#     Сериализатор для модели Список покупок. Обрабатывает информацию о
#     рецептах, добавленных в список покупок.
#     """

#     class Meta:
#         model = ShoppingList
#         fields = ['user', 'recipes']


# class FavoriteSerializer(serializers.ModelSerializer):
#     """Сериализатор для модели Favorite"""
#     class Meta:
#         model = FavoriteRecipe
#         fields = ['user', 'recipe', 'created_at']

#     # def to_internal_value(self, data):
#     #     """Добавление кастомной логики для сериализации картинки"""
#     #     if 'image' in data:
#     #         image_data = base64.b64decode(data['image'])
#     #         file_name = 'image.png'
#     #         data['image'] = ContentFile(image_data, name=file_name)
#     #     return super().to_internal_value(data)


# class FollowSerializer(UserSerializer):
#     """Сериализатор для модели Follow."""

#     recipes = serializers.SerializerMethodField(
#         read_only=True,
#         method_name='get_recipes')
#     recipes_count = serializers.SerializerMethodField(
#         read_only=True
#     )

#     class Meta:
#         """Мета-параметры сериализатора"""

#         model = User
#         fields = ('email', 'id', 'username', 'first_name',
#                   'last_name', 'recipes')

#     # def get_recipes(self, obj):
#     #     """Метод для получения рецептов"""

#     #     request = self.context.get('request')
#     #     recipes = obj.recipes.all()
#     #     recipes_limit = request.query_params.get('recipes_limit')
#     #     if recipes_limit:
#     #         recipes = recipes[:int(recipes_limit)]
#     #     return AdditionalForRecipeSerializer(recipes, many=True).data

#     @staticmethod
#     def get_recipes_count(obj):
#         """Метод для получения количества рецептов"""

#         return obj.recipes.count()


# # class RecipeImageSerializer(serializers.ModelSerializer):
# #     """Сериализатор для работы с изображениями"""
# #     class Meta:
# #         model = FavoriteRecipe
# #         fields = ['title', 'image']

# #     def to_internal_value(self, data):
# #         if 'image' in data:
# #             image_data = base64.b64decode(data['image'])
# #             file_name = 'recipe_image.png'
# #             data['image'] = ContentFile(image_data, name=file_name)
# #         return super().to_internal_value(data)


# # class RecipeSerializer(serializers.ModelSerializer):
# #     """Сериализатор для модели Рецепт"""
# #     ingredients = IngredientSerializer(many=True)
# #     tags = TagSerializer(many=True)
# #     image = serializers.ImageField(write_only=True)

# #     class Meta:
# #         model = Recipe
# #         fields = ['id',
# #                   'title',
# #                   'author',
# #                   'description',
# #                   'ingredients',
# #                   'tags',
# #                   'cooking_time',
# #                   'image']

# #     def create(self, validated_data):
# #         """Кастомная логика для создания рецепта"""
# #         ingredients_data = validated_data.pop('ingredients')
# #         tags_data = validated_data.pop('tags')
# #         recipe = Recipe.objects.create(**validated_data)

# #         for ingredient_data in ingredients_data:
# #             ingredient = Ingredient.objects.create(**ingredient_data)
# #             recipe.ingredients.add(ingredient)

# #         for tag_data in tags_data:
# #             tag = Tag.objects.create(**tag_data)
# #             recipe.tags.add(tag)

# #         return recipe

# #     def to_internal_value(self, data):
# #         """Кастомная обработка изображения base64"""
# #         image_data = data.get('image', None)
# #         if image_data:
# #             format, imgstr = image_data.split(';base64,')
# #             ext = format.split('/')[-1]
# #             img_data = base64.b64decode(imgstr)
# #             file_name = 'recipe_image.' + ext
# #             file = ContentFile(img_data, file_name)
# #             data['image'] = file
# #         return super().to_internal_value(data)
