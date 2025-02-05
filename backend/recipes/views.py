from rest_framework import viewsets, permissions, filters, status
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.permissions import (
    AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
)
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from recipes.filters import IngredientFilter
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from .models import User, Recipe, Tag, Ingredient, FavoriteRecipe, ShoppingList
from .serializers import (
    UserSerializer, RecipeSerializer, TagSerializer,
    IngredientSerializer, FavoriteRecipeSerializer,
    ShoppingListSerializer
)
from .pagination import CustomPagination
from rest_framework.pagination import LimitOffsetPagination


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
    


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination
    # permission_classes = [permissions.AllowAny]

    def get_serializer_context(self):
        """Передаем request в контекст сериализатора"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_queryset(self):
        """Фильтруем рецепты по избранному, если передан параметр favorite=true"""
        queryset = Recipe.objects.all()
        request = self.request
        is_favorited = request.query_params.get("is_favorited")
        if request.user.is_authenticated and is_favorited == "1":
            queryset = queryset.filter(favorite_recipes__user=request.user)
        return queryset


    



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
            # Добавление рецепта в избранное
            FavoriteRecipe.objects.get_or_create(user=request.user, recipe=recipe)
            return Response({'status': 'Рецепт добавлен в избранное'})
        
        elif request.method == 'DELETE':
            # Удаление рецепта из избранного
            favorite = FavoriteRecipe.objects.filter(user=request.user, recipe=recipe)
            if favorite.exists():
                favorite.delete()
                return Response({'status': 'Рецепт удалён из избранного'}, status=status.HTTP_204_NO_CONTENT)
            return Response({'error': 'Рецепт не найден в избранном'}, status=status.HTTP_400_BAD_REQUEST)

    # @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    # def favorite(self, request, pk=None):
    #     """Добавление рецепта в избранное"""
    #     recipe = get_object_or_404(Recipe, pk=pk)
    #     FavoriteRecipe.objects.get_or_create(user=request.user, recipe=recipe)
    #     return Response({'status': 'Рецепт добавлен в избранное'})
    
    # @action(detail=True, methods=['delete'], permission_classes=[permissions.IsAuthenticated])
    # def unfavorite(self, request, pk=None):
    #     """Удаление рецепта из избранного"""
    #     recipe = get_object_or_404(Recipe, pk=pk)
    #     favorite = FavoriteRecipe.objects.filter(user=request.user, recipe=recipe)
    #     if favorite.exists():
    #         favorite.delete()
    #         return Response({'status': 'Рецепт удалён из избранного'}, status=status.HTTP_204_NO_CONTENT)
    #     return Response({'error': 'Рецепт не найден в избранном'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        """Добавление рецепта в список покупок"""
        recipe = get_object_or_404(Recipe, pk=pk)
        ShoppingList.objects.get_or_create(user=request.user, recipe=recipe)
        return Response({'status': 'Рецепт добавлен в список покупок'})

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
