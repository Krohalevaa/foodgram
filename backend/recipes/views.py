from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from .models import User, Recipe, Tag, Ingredient, FavoriteRecipe, ShoppingList
from .serializers import (
    UserSerializer, RecipeSerializer, TagSerializer,
    IngredientSerializer, FavoriteRecipeSerializer,
    ShoppingListSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=False, 
            methods=['get'], 
            permission_classes=[permissions.AllowAny])
            # permission_classes=[IsAuthenticated])
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        """Добавление рецепта в избранное"""
        recipe = get_object_or_404(Recipe, pk=pk)
        FavoriteRecipe.objects.get_or_create(user=request.user, recipe=recipe)
        return Response({'status': 'Рецепт добавлен в избранное'})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def add_to_shopping_list(self, request, pk=None):
        """Добавление рецепта в список покупок"""
        recipe = get_object_or_404(Recipe, pk=pk)
        ShoppingList.objects.get_or_create(user=request.user, recipe=recipe)
        return Response({'status': 'Рецепт добавлен в список покупок'})


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = FavoriteRecipe.objects.all()
    serializer_class = FavoriteRecipeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class ShopListViewSet(viewsets.ModelViewSet):
    queryset = ShoppingList.objects.all()
    serializer_class = ShoppingListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
