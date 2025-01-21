from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Recipe, Tag, Ingredient
from .serializers import RecipeSerializer, TagSerializer, IngredientSerializer
from rest_framework.permissions import IsAuthenticated


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Рецепт"""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]

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


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Ингредиент"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
