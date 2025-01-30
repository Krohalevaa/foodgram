# from django.shortcuts import render

from rest_framework import viewsets
# status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
# BasePermission, IsAuthenticated

# from rest_framework import generics, permissions
# from rest_framework.viewsets import ModelViewSet
# from rest_framework.pagination import PageNumberPagination

# from .models import Recipe, Tag, Ingredient, FavoriteRecipe, ShoppingList


# from django.db.models import Sum
# from django.http import HttpResponse
# from django.shortcuts import get_object_or_404
# # from django_filters.rest_framework import DjangoFilterBackend
# from djoser.views import UserViewSet


# from rest_framework.pagination import LimitOffsetPagination
# from rest_framework.permissions import (
#     AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
# )

# from .filters import IngredientFilter, RecipeFilter
# from .pagination import CustomPagination
# from .permissions import IsAuthorOrReadOnly
from .serializers import (RecipeSerializer,
                          TagSerializer, IngredientSerializer, ShopListSerializer,
                          FavoriteSerializer)
# Base64ImageField, RecipeIngredientSerializer, CreateRecipeIngredientSerializer, CreateRecipeSerializer, UserSerializer, UserCreateSerializer, FollowSerializer)

from .models import (Recipe, Tag, Ingredient,
                     FavoriteRecipe, ShoppingList)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Рецепт"""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]
    # filter_backends = (DjangoFilterBackend,)
    # filterset_class = RecipeFilter

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        """Добавить рецепт в избранное"""
        recipe = self.get_object()
        user = request.user
        user.favorites.add(recipe)
        return Response({"status": "recipe added to favorites"})

    @action(detail=True, methods=['post'])
    def subscribe(self, request, pk=None):
        """Подписаться на автора рецепта"""
        recipe = self.get_object()
        user = request.user
        user.subscriptions.add(recipe.author)
        return Response({"status": "subscribed to author"})

    @action(detail=True, methods=['post'])
    def add_to_shoplist(self, request, pk=None):
        """Добавить рецепт в список покупок"""
        recipe = self.get_object()
        user = request.user
        user.shoplist.add(recipe)
        return Response({"status": "recipe added to shopping list"})


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Тег"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    # permission


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Ингредиент"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    # permission_classes = (AllowAny,)
    # filter_backends = (DjangoFilterBackend,)
    # filterset_class = IngredientFilter
    # search_fields = ('^name',)


# class UserViewSet(viewsets.ModelViewSet):
#     """Вьюсет для управления пользователями. Поддерживает CRUD."""
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     # permission_classes = [IsOwnerOrReadOnly]

#     # @action(detail=True,
#     #         methods=['post'],
#     #         serializer_class=UserAvatarSerializer)
#     # def change_avatar(self, request, pk=None):
#     #     """Кастомное действие для изменения фото пользователя."""
#     #     user = self.get_object()
#     #     serializer = UserAvatarSerializer(data=request.data)
#     #     if serializer.is_valid():
#     #         user.avatar = serializer.validated_data['avatar']
#     #         user.save()
#     #         return Response({"status": "avatar updated"})
#     #     return Response(serializer.errors, status=400)

#     # @action(detail=True, methods=['post'])
#     # def subscribe(self, request, pk=None):
#     #     """Кастомное действие для подписки на пользователя."""
#     #     user_to_subscribe = self.get_object()
#     #     user = request.user
#     #     if user == user_to_subscribe:
#     #         return Response({"error": "Cannot subscribe to yourself"},
#     #                         status=400)
#     #     user.subscriptions.add(user_to_subscribe)
#     #     return Response({"status": "subscribed successfully"})

#     # @action(detail=True, methods=['post'])
#     # def unsubscribe(self, request, pk=None):
#     #     """Кастомное действие для отписки от пользователя."""
#     #     user_to_unsubscribe = self.get_object()
#     #     user = request.user
#     #     user.subscriptions.remove(user_to_unsubscribe)
#     #     return Response({"status": "unsubscribed successfully"})


class ShopListViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с моделью Список покупок (CRUD)"""
    queryset = ShoppingList.objects.all()
    serializer_class = ShopListSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def add_to_shoplist(self, request, pk=None):
        """Добавление рецепта в список покупок."""
        shoplist = self.get_object()
        recipe = Recipe.objects.get(pk=pk)
        shoplist.recipes.add(recipe)
        return Response({'status': 'recipe added to shopping list'})

    @action(detail=True, methods=['post'])
    def remove_from_shoplist(self, request, pk=None):
        """Удаление рецепта из списка покупок."""
        shoplist = self.get_object()
        recipe = Recipe.objects.get(pk=pk)
        shoplist.recipes.remove(recipe)
        return Response({'status': 'recipe removed from shopping list'})


class FavoriteViewSet(viewsets.ModelViewSet):
    """Вьюсет для избранного"""
    queryset = FavoriteRecipe.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='add_to_favorites')
    def add_to_favorites(self, request):
        user = request.user
        recipe_id = request.data.get('recipe_id')
        recipe = FavoriteRecipe.objects.get(id=recipe_id)
        favorite, created = FavoriteRecipe.objects.get_or_create(user=user,
                                                                 recipe=recipe)
        if created:
            return Response({"status": "added to favorites"})
        return Response({"status": "already in favorites"})

    @action(detail=False, methods=['get'], url_path='user_favorites')
    def user_favorites(self, request):
        user = request.user
        favorites = FavoriteRecipe.objects.filter(user=user)
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data)
