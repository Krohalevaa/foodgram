from rest_framework import viewsets
from .models import ShopList, Recipe
from .serializers import ShopListSerializer, RecipeSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """Класс для пагинации."""
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100


class ShopListViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с моделью Список покупок (CRUD)"""

    queryset = ShopList.objects.all()
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

class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с моделью Рецепт (CRUD)."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def add_to_favorites(self, request, pk=None):
        """
        Добавление рецепта в избранное.
        """
        # Добавление рецепта в избранное пользователя
        pass

    @action(detail=True, methods=['post'])
    def subscribe(self, request, pk=None):
        """
        Подписка на рецепты автора.
        """
        # Подписка на автора рецепта
        pass
