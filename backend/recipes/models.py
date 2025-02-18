"""Модуль моделей для работы с рецептами и подписками."""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from slugify import slugify

from recipes.constants import (MAX_LENGHT_NAME, MAX_LENGHT_NAME_TAG,
                               MAX_LENGHT_NAME_TEXT, MAX_LENGHT_UNIT)
from users.models import User


class Ingredient(models.Model):
    """Модель ингредиента.

    Эта модель используется для хранения информации о ингредиентах,
    которые могут быть использованы в рецептах.
    Включает название ингредиента и его единицу измерения.
    """

    name = models.CharField(
        max_length=MAX_LENGHT_NAME,
        verbose_name='Название ингредиента')
    unit = models.CharField(
        max_length=MAX_LENGHT_UNIT,
        verbose_name='Единица измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тега рецепта.

    Эта модель используется для хранения тегов, которые могут быть
    присвоены рецептам.
    Каждый тег имеет уникальное название и слаг, а также цвет в формате HEX.
    """

    name = models.CharField(
        max_length=MAX_LENGHT_NAME_TAG,
        unique=True,
        verbose_name='Название тэга записи')
    slug = models.SlugField(
        max_length=MAX_LENGHT_NAME_TAG,
        unique=True,
        verbose_name='Слаг')
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет в HEX',
        default='#FFFFFF')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель для страницы рецепта пользователя.

    Эта модель используется для хранения рецептов, включая название,
    описание, фото, время приготовления, автора, связанные теги и ингредиенты.
    Каждый рецепт также имеет уникальный слаг и дату создания.
    """

    name = models.CharField(
        max_length=MAX_LENGHT_NAME,
        verbose_name='Заголовок рецепта')
    text = models.TextField(
        max_length=MAX_LENGHT_NAME_TEXT,
        verbose_name='Описание рецепта')
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Фото рецепта',
        blank=True)
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления рецепта в минутах',
        validators=[MinValueValidator(1), MaxValueValidator(1440)])
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',)
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тэги рецепта',)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты в рецепте')
    slug = models.SlugField(
        unique=True,
        blank=True)
    creation_date = models.DateField(
        auto_now_add=True,
        verbose_name='Дата создания рецепта')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('creation_date',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Переопределяет метод сохранения.

        Для того, чтобы генерировать уникальный слаг для рецепта.
        Если слаг не задан, он создается автоматически на основе
        названия рецепта.
        """
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Recipe.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class RecipeIngredient(models.Model):
    """Модель для связи между рецептом и ингредиентом.

    Эта модель используется для хранения информации о том, какие
    ингредиенты используются в рецепте, и в каком количестве.
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт',)
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='ingredient_recipes',)
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиента',
        validators=[MinValueValidator(1), MaxValueValidator(10000)])

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'

    def __str__(self):
        return (
            f'{self.amount} {self.ingredient.unit} of {self.ingredient.name}')


class FavoriteRecipe(models.Model):
    """Модель для избранных рецептов пользователя.

    Эта модель используется для хранения избранных рецептов
    конкретного пользователя.
    Один пользователь может добавить один рецепт в избранное только один раз.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
        verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited_by_users',
        verbose_name='Рецепт')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f'{self.user.username} -> {self.recipe.name}'


class ShoppingList(models.Model):
    """Модель для списка покупок пользователя.

    Эта модель используется для хранения рецептов, которые
    добавлены пользователем в список покупок.
    Один пользователь может добавить один рецепт в список покупок
    только один раз.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_lists',
        verbose_name='Рецепт')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f'Список покупок для {self.user.username}: {self.recipe.name}'


class Subscription(models.Model):
    """Модель для подписки пользователей.

    Эта модель используется для хранения информации о подписках пользователей
    на других пользователей (авторов рецептов).
    Один пользователь может подписаться на другого пользователя.
    """

    author = models.ForeignKey(
        User,
        related_name='subscribers',
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта')
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.author} -> {self.subscriber}'
