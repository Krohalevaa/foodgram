"""Модуль вью для работы с рецептаци и пользователями."""

from http import HTTPStatus

from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import (FavoriteRecipe, Ingredient, Recipe, ShoppingList,
                            Subscription, Tag)
from users.models import User

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination, UserPagination
from .serializers import (CustomUserCreateSerializer, FavoriteRecipeSerializer,
                          IngredientSerializer, RecipeSerializer,
                          ShoppingListSerializer, SubscriptionSerializer,
                          TagSerializer, UserSerializer)


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с ингредиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    http_method_names = ['get', 'post', 'head', 'options', 'delete']

    def create(self, request, *args, **kwargs):
        """Запрещаем создание ингредиента."""
        raise MethodNotAllowed('POST')


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с тегами рецептов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        """Переопределение метода создания."""
        if Tag.objects.filter(name=request.data.get('name')).exists():
            raise MethodNotAllowed('Method Not Allowed')
        if Tag.objects.filter(slug=request.data.get('slug')).exists():
            raise MethodNotAllowed('Method Not Allowed')
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Обработка ошибки, для обновления."""
        raise MethodNotAllowed('PUT')


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

    lookup_field = 'pk'
    queryset = User.objects.annotate(recipes_count=Count('recipes'))
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = UserPagination

    def create(self, request, *args, **kwargs):
        """Создание пользователя с хешированным паролем."""
        serializer = CustomUserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login_url = '/signin/'
            return Response(UserSerializer(user).data,
                            status=status.HTTP_201_CREATED,
                            headers={'Location': login_url})
        return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.AllowAny])
    def me(self, request):
        """Получение информации о текущем пользователе."""
        if not request.user.is_authenticated:
            return Response({
                'detail': 'Учетные данные не были предоставлены.'},
                status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def set_password(self, request):
        """Изменение пароля текущего пользователя."""
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        if not current_password or not new_password:
            return Response({'error': 'Текущий и новый пароли обязательны'},
                            status=HTTPStatus.BAD_REQUEST)
        if not user.check_password(current_password):
            return Response({'error': 'Неверный текущий пароль'},
                            status=HTTPStatus.BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        return Response(status=HTTPStatus.NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, pk=None):
        """Подписка или отписка от пользователя."""
        if request.method == 'POST':
            author = get_object_or_404(User, pk=pk)
            if Subscription.objects.filter(subscriber=request.user,
                                           author=author).exists():
                return Response(
                    {'error': f'Вы уже подписаны на {author.username}'},
                    status=HTTPStatus.BAD_REQUEST
                )
            data = {'author': author.id, 'subscriber': request.user.id}
            serializer = SubscriptionSerializer(
                data=data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {'status': f'Вы подписались на {author.username}'},
                    status=HTTPStatus.CREATED)
            return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)

        elif request.method == 'DELETE':
            deleted_count, _ = Subscription.objects.filter(
                author__pk=pk, subscriber=request.user).delete()
            if deleted_count:
                return Response(
                    {'status': f'Вы отписались от пользователя с ID {pk}'},
                    status=HTTPStatus.NO_CONTENT)
            return Response(
                {'error': f'Вы не подписаны на пользователя с ID {pk}'},
                status=HTTPStatus.BAD_REQUEST)

    @action(detail=True,
            methods=['get'],
            permission_classes=[permissions.AllowAny])
    def recipes(self, request, pk=None):
        """Все рецепты пользователя."""
        user = get_object_or_404(User, pk=pk)
        recipes = Recipe.objects.filter(author=user)
        serializer = RecipeSerializer(
            recipes,
            many=True,
            context={'request': request})
        return Response(serializer.data)

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """Возвращает список подписок для текущего пользователя."""
        subscriptions = Subscription.objects.filter(subscriber=request.user)
        serializer = SubscriptionSerializer(
            subscriptions,
            many=True,
            context={'request': request})
        recipes_limit = request.query_params.get('recipes_limit')
        context = self.get_serializer_context()
        context.update({'recipes_limit': recipes_limit})
        page = self.paginate_queryset(subscriptions)
        if page is not None:
            serializer = SubscriptionSerializer(
                page,
                many=True,
                context=context)
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionSerializer(
            subscriptions,
            many=True,
            context=context)
        return Response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами."""

    queryset = Recipe.objects.select_related('author').prefetch_related(
        'tags', 'ingredients')
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = RecipeFilter
    ordering_fields = ['creation_date']
    ordering = ['-creation_date', '-id']

    def perform_create(self, serializer):
        """Автоматически устанавливаем текущего пользователя как автора."""
        serializer.save(author=self.request.user)

    def get_serializer_context(self):
        """Передача request в контекст сериализатора."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        """Фильтруем рецепты по избранному и списку покупок."""
        queryset = Recipe.objects.all().order_by('-creation_date', '-id')
        request = self.request
        is_favorited = request.query_params.get('is_favorited')
        if request.user.is_authenticated and is_favorited == '1':
            queryset = queryset.filter(favorited_by_users__user=request.user)
        is_in_shopping_cart = request.query_params.get('is_in_shopping_cart')
        if request.user.is_authenticated and is_in_shopping_cart == '1':
            queryset = queryset.filter(shopping_lists__user=request.user)
        return queryset

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        """Добавление/удаление рецепта из списка покупок."""
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, pk=pk)
            data = {'user': request.user.id, 'recipe': recipe.id}
            serializer = ShoppingListSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response(
                    {'status': 'Рецепт добавлен в список покупок'},
                    status=HTTPStatus.CREATED)
            return Response(
                {'error': 'Рецепт уже в списке покупок'},
                status=HTTPStatus.BAD_REQUEST)

        elif request.method == 'DELETE':
            deleted_count, _ = ShoppingList.objects.filter(
                user=request.user,
                recipe_id=pk).delete()
            if deleted_count:
                return Response(
                    {'status': 'Рецепт удалён из списка покупок'},
                    status=HTTPStatus.NO_CONTENT)
            return Response(
                {'error': 'Рецепт не найден в списке покупок'},
                status=HTTPStatus.BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        """Получение короткой ссылки на рецепт."""
        recipe = self.get_object()
        return Response({'short_link': f'/api/recipes/{recipe.slug}/'})

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        """Добавление или удаление рецепта в/из избранного."""
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            if FavoriteRecipe.objects.filter(user=request.user,
                                             recipe=recipe).exists():
                return Response(
                    {'error': 'Рецепт уже в избранном'},
                    status=status.HTTP_400_BAD_REQUEST)
            data = {'user': request.user.id, 'recipe': recipe.id}
            serializer = FavoriteRecipeSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {'status': 'Рецепт добавлен в избранное'},
                    status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            deleted_count, _ = FavoriteRecipe.objects.filter(
                user=request.user, recipe_id=pk).delete()
            if deleted_count:
                return Response(
                    {'status': 'Рецепт удалён из избранного'},
                    status=status.HTTP_204_NO_CONTENT
                )
            return Response(
                {'error': 'Рецепт не найден в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def create_recipe(request):
        """Создание нового рецепта, доступ к ингредиентам."""
        ingredients = Ingredient.objects.all()
        return render(request,
                      'recipes/create_recipe.html',
                      {'ingredients': ingredients})

    @action(detail=True, methods=['get'])
    def get_ingredients(self, request, pk=None):
        """Возвращает ингредиенты рецепта."""
        recipe = self.get_object()
        ingredients = recipe.ingredients.all()
        ingredients_serializer = IngredientSerializer(ingredients, many=True)
        return Response(ingredients_serializer.data)

    @action(detail=False, methods=['get'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request, *args, **kwargs):
        """Скачивание списка покупок для текущего пользователя."""
        shopping_list = ShoppingList.objects.filter(user=request.user)
        ingredients = self.get_ingredients_from_shopping_list(shopping_list)
        content = self.generate_shopping_cart_content(ingredients)

        response = HttpResponse(content, content_type='text/plain')
        response[
            'Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response

    def get_ingredients_from_shopping_list(self, shopping_list):
        """Извлекает ингредиенты из корзины покупок пользователя."""
        ingredients = (
            Ingredient.objects
            .filter(
                ingredient_recipes__recipe__shopping_lists__user=(
                    self.request.user)
            )
            .annotate(total_amount=Sum('ingredient_recipes__amount'))
            .values('name', 'unit', 'total_amount')
        )

        return {
            f"{ingredient['name']} ({ingredient['unit']})":
            ingredient['total_amount']
            for ingredient in ingredients
        }

    def generate_shopping_cart_content(self, ingredients):
        """Генерирует контент для скачивания в виде текста."""
        return '\n'.join(
            f'{name} — {amount}' for name, amount in ingredients.items())


class FavoriteViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с избранными рецептами пользователя."""

    serializer_class = FavoriteRecipeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Возвращает избранные рецепты для текущего пользователя."""
        return FavoriteRecipe.objects.filter(user=self.request.user)


class ShopListViewSet(viewsets.ModelViewSet):
    """Представление для работы с списками покупок."""

    serializer_class = ShoppingListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Возвращает список покупок для текущего пользователя."""
        return ShoppingList.objects.filter(user=self.request.user)
