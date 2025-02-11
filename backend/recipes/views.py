from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination

from django.shortcuts import get_object_or_404, render
from django_filters.rest_framework import DjangoFilterBackend
from recipes.filters import IngredientFilter, RecipeFilter
from django.http import HttpResponse


from .models import User, Recipe, Tag, Ingredient, FavoriteRecipe, ShoppingList, Subscription
from .serializers import (
    UserSerializer, RecipeSerializer, TagSerializer,
    IngredientSerializer, FavoriteRecipeSerializer,
    ShoppingListSerializer, SubscriptionSerializer
)
from .pagination import CustomPagination
from collections import defaultdict


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]


class UserAvatarUpdateView(generics.UpdateAPIView):
    """Эндпоинт для обновления аватара пользователя."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = LimitOffsetPagination

    @action(detail=False,
            methods=['get'],
            permission_classes=[permissions.AllowAny])
            # permission_classes=[IsAuthenticated])
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def set_password(self, request):
        user = request.user
        new_password = request.data.get("new_password")
        if not new_password:
            return Response({"error": "Новый пароль обязателен"}, status=400)
        user.set_password(new_password)
        user.save()
        return Response({"status": "Пароль успешно изменён"}, status=200)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, pk=None):
        """Подписка на пользователя"""
        author = get_object_or_404(User, pk=pk)
        if request.user == author:
            return Response({"error": "Нельзя подписаться на самого себя."}, status=status.HTTP_400_BAD_REQUEST)

        subscription, created = Subscription.objects.get_or_create(author=author, subscriber=request.user)
        if created:
            return Response({"status": f"Вы подписались на {author.username}"}, status=status.HTTP_201_CREATED)
        return Response({"status": f"Вы уже подписаны на {author.username}"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def unsubscribe(self, request, pk=None):
        """Отписка от пользователя"""
        author = get_object_or_404(User, pk=pk)
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
        """
        Возвращает список подписок для текущего пользователя.
        Поддерживает параметр recipes_limit для ограничения количества рецептов.
        """
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
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        """При создании рецепта автоматически устанавливаем текущего пользователя как автора"""
        serializer.save(author=self.request.user)

    def get_serializer_context(self):
        """Передаем request в контекст сериализатора"""
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
        recipe = self.get_object()
        return Response({"short_link": f"/api/recipes/{recipe.slug}/"})

    @action(detail=True, methods=['post', 'delete'], permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        """Добавление или удаление рецепта в/из избранного.
        POST - добавление,
        DELETE - удаление."""
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
    queryset = FavoriteRecipe.objects.all()
    serializer_class = FavoriteRecipeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class ShopListViewSet(viewsets.ModelViewSet):
    serializer_class = ShoppingListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ShoppingList.objects.filter(user=self.request.user)
