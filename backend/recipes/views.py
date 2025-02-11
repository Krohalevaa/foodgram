from collections import defaultdict

from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination

from django.shortcuts import get_object_or_404, render
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth import authenticate, get_user_model

from .models import User, Recipe, Tag, Ingredient, FavoriteRecipe, ShoppingList, Subscription
from .serializers import (UserSerializer, RecipeSerializer, TagSerializer,
                          IngredientSerializer, FavoriteRecipeSerializer,
                          ShoppingListSerializer, SubscriptionSerializer, UserCreateSerializer)
from .pagination import CustomPagination
from recipes.filters import IngredientFilter, RecipeFilter


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с ингредиентами."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с тегами рецептов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]


class UserAvatarUpdateView(generics.UpdateAPIView):
    """Для обновления аватара пользователя."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Возвращает текущего пользователя для обновления аватара."""
        return self.request.user

    def put(self, request, *args, **kwargs):
        """Частичное обновление пользователя, включая аватар."""
        return self.partial_update(request, *args, **kwargs)


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с пользователями."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = LimitOffsetPagination

    def create(self, request, *args, **kwargs):
        """Создание пользователя с хешированным паролем"""
        serializer = UserCreateSerializer(data=request.data)  # Используем UserCreateSerializer для создания пользователя
        if serializer.is_valid():
            user = serializer.save()  # Сохраняем пользователя через сериализатор
            # Перенаправляем пользователя на страницу входа после регистрации
            login_url = reverse('login')  # Или укажите свой URL для страницы входа
            return Response({'message': 'Пользователь успешно создан. Перенаправление на страницу входа.'}, status=status.HTTP_201_CREATED, headers={'Location': login_url})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def create(self, request, *args, **kwargs):
    #     """Создание пользователя с хешированным паролем"""
    #     serializer = UserCreateSerializer(data=request.data)  # Используем UserCreateSerializer для создания пользователя
    #     if serializer.is_valid():
    #         user = serializer.save()  # Сохраняем пользователя через сериализатор
    #         return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def me(self, request):
        """Получение информации о текущем пользователе."""
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def set_password(self, request):
        """Изменение пароля текущего пользователя."""
        user = request.user
        new_password = request.data.get("new_password")
        if not new_password:
            return Response({"error": "Новый пароль обязателен"}, status=400)
        user.set_password(new_password)
        user.save()
        return Response({"status": "Пароль успешно изменён"}, status=200)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, pk=None):
        """Подписка или отписка от пользователя."""
        author = get_object_or_404(User, pk=pk)

        if request.user == author:
            return Response({"error": "Нельзя подписаться или отписаться от самого себя."}, status=status.HTTP_400_BAD_REQUEST)

        # POST запрос - подписка
        if request.method == 'POST':
            subscription, created = Subscription.objects.get_or_create(author=author, subscriber=request.user)
            if created:
                return Response({"status": f"Вы подписались на {author.username}"}, status=status.HTTP_201_CREATED)
            return Response({"status": f"Вы уже подписаны на {author.username}"}, status=status.HTTP_400_BAD_REQUEST)

        # DELETE запрос - отписка
        elif request.method == 'DELETE':
            subscription = Subscription.objects.filter(author=author, subscriber=request.user)
            if subscription.exists():
                subscription.delete()
                return Response({"status": f"Вы отписались от {author.username}"}, status=status.HTTP_204_NO_CONTENT)
            return Response({"error": f"Вы не подписаны на {author.username}"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def recipes(self, request, pk=None):
        """Все рецепты пользователя"""
        user = get_object_or_404(User, pk=pk)
        recipes = Recipe.objects.filter(author=user)
        serializer = RecipeSerializer(recipes, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """Возвращает список подписок для текущего пользователя."""
        subscriptions = Subscription.objects.filter(subscriber=request.user)
        serializer = SubscriptionSerializer(subscriptions, many=True, context={'request': request})
        recipes_limit = request.query_params.get('recipes_limit')
        context = self.get_serializer_context()
        context.update({'recipes_limit': recipes_limit})
        page = self.paginate_queryset(subscriptions)
        if page is not None:
            serializer = SubscriptionSerializer(page, many=True, context=context)
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionSerializer(subscriptions, many=True, context=context)
        return Response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        """
        При создании рецепта автоматически устанавливаем
        текущего пользователя как автора
        """
        serializer.save(author=self.request.user)

    def get_serializer_context(self):
        """Передача request в контекст сериализатора"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        """Фильтруем рецепты по избранному и списку покупок"""
        queryset = Recipe.objects.all()
        request = self.request
        is_favorited = request.query_params.get("is_favorited")
        if request.user.is_authenticated and is_favorited == "1":
            queryset = queryset.filter(favorited_by_users__user=request.user)
        is_in_shopping_cart = request.query_params.get("is_in_shopping_cart")
        if request.user.is_authenticated and is_in_shopping_cart == "1":
            queryset = queryset.filter(shopping_lists__user=request.user)
        return queryset

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        """Добавление/удаление рецепта из списка покупок."""
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            obj, created = ShoppingList.objects.get_or_create(user=request.user, recipe=recipe)
            if created:
                return Response({'status': 'Рецепт добавлен в список покупок'}, status=status.HTTP_201_CREATED)
            return Response({'error': 'Рецепт уже в списке покупок'}, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            deleted_count, _ = ShoppingList.objects.filter(user=request.user, recipe=recipe).delete()
            if deleted_count:
                return Response({'status': 'Рецепт удалён из списка покупок'}, status=status.HTTP_204_NO_CONTENT)
            return Response({'error': 'Рецепт не найден в списке покупок'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        """Получение короткой ссылки на рецепт."""
        recipe = self.get_object()
        return Response({"short_link": f"/api/recipes/{recipe.slug}/"})

    @action(detail=True, methods=['post', 'delete'], permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        """Добавление или удаление рецепта в/из избранного."""
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            FavoriteRecipe.objects.get_or_create(user=request.user, recipe=recipe)
            return Response({'status': 'Рецепт добавлен в избранное'})
        elif request.method == 'DELETE':
            favorite = FavoriteRecipe.objects.filter(user=request.user, recipe=recipe)
            if favorite.exists():
                favorite.delete()
                return Response({'status': 'Рецепт удалён из избранного'}, status=status.HTTP_204_NO_CONTENT)
            return Response({'error': 'Рецепт не найден в избранном'}, status=status.HTTP_400_BAD_REQUEST)

    def create_recipe(request):
        """Создание нового рецепта, доступ к ингредиентам."""
        ingredients = Ingredient.objects.all()
        return render(request, 'recipes/create_recipe.html', {'ingredients': ingredients})

    @action(detail=True, methods=['get'])
    def get_ingredients(self, request, pk=None):
        """Возвращает ингредиенты рецепта"""
        recipe = self.get_object()
        ingredients = recipe.ingredients.all()
        ingredients_serializer = IngredientSerializer(ingredients, many=True)
        return Response(ingredients_serializer.data)

    @action(detail=False, methods=['get'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request, *args, **kwargs):
        """Скачивание списка покупок для текущего пользователя."""
        shopping_list = ShoppingList.objects.filter(user=request.user)
        ingredients = defaultdict(float)
        for item in shopping_list:
            for recipe_ingredient in item.recipe.recipe_ingredients.all():
                ingredient = recipe_ingredient.ingredient
                ingredients[f"{ingredient.name} ({ingredient.unit})"] += recipe_ingredient.amount
        content = "\n".join(f"{name} — {amount}" for name, amount in ingredients.items())
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response


class FavoriteViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с избранными рецептами пользователя."""
    queryset = FavoriteRecipe.objects.all()
    serializer_class = FavoriteRecipeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Возвращает избранные рецепты для текущего пользователя."""
        return self.queryset.filter(user=self.request.user)


class ShopListViewSet(viewsets.ModelViewSet):
    """Представление для работы с списками покупок."""
    serializer_class = ShoppingListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Возвращает список покупок для текущего пользователя."""
        return ShoppingList.objects.filter(user=self.request.user)
