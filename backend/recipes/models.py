from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.urls import reverse
# from django.utils.text import slugify
from django.core.validators import MinValueValidator
# , RegexValidator


class User(AbstractUser):
    """Модель для пользователя, расширяющая стандартную модель AbstractUser."""
    email = models.EmailField(
        unique=True,
        max_length=50,
        verbose_name='Электронная почта')
    username = models.CharField(
        unique=True,
        max_length=50,
        verbose_name='Никнейм пользователя')
    first_name = models.CharField(
        max_length=50,
        verbose_name='Имя пользователя')
    last_name = models.CharField(
        max_length=50,
        verbose_name='Фамилия пользователя')
    bio: models.TextField = models.TextField(
        max_length=150,
        verbose_name='Описание пользователя')
    # avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions_set',
        blank=True,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        """Мета-параметры модели"""
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username


class Recipe(models.Model):
    """Модель для страницы рецепта пользователя."""
    title: models.CharField = models.CharField(
        max_length=255,
        verbose_name='Заголовок рецепта')
    description: models.TextField = models.TextField(
        max_length=255,
        verbose_name='Описание рецепта',
        blank=True,
        null=True)
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Фото рецепта',
        blank=True)
    preparation_time: models.PositiveIntegerField = models.PositiveIntegerField(
        verbose_name='Время приготовления рецепта в минутах',)
    author: models.ForeignKey = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',)
    tags: models.ManyToManyField = models.ManyToManyField(
        'Tag',
        related_name='recipes',
        verbose_name='Тэги рецепта',)
    ingredients: models.ManyToManyField = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингридиенты')
    slug: models.SlugField = models.SlugField(
        unique=True,
        blank=True)
    creation_date: models.DateTimeField = models.DateTimeField(
        # auto_now_add=True,
        # db_index=True,
        verbose_name='Дата создания рецепта'
    )

    class Meta:
        """Мета-параметры модели"""
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('creation_date',)

    def get_short_link(self):
        """Возвращает короткую ссылку на рецепт."""
        return reverse('recipe_detail', kwargs={'slug': self.slug})

    # def save(self, *args, **kwargs):
    #     """Переопределенный метод сохранения экземпляра модели."""
    #     if not self.slug:
    #         self.slug = slugify(self.title)
    #     super().save(*args, **kwargs)

    def __str__(self):
        """Возвращает строковое представление рецепта."""
        return self.title


class Tag(models.Model):
    """Модель для тега записи."""
    name: models.CharField = models.CharField(
        max_length=35,
        unique=True,
        verbose_name='Название тэга записи')
    slug: models.SlugField = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name='Слаг')

    class Meta:
        """Мета-параметры модели"""
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        """Возвращает строковое представление тега."""
        return self.name


class Ingredient(models.Model):
    """
    Модель для ингредиента.
    """
    name: models.CharField = models.CharField(
        max_length=100,
        verbose_name='Название ингредиента')
    unit: models.CharField = models.CharField(
        max_length=50,
        verbose_name='Единица измерения')  # Ед: граммы, литры, шт.

    class Meta:
        """Мета-параметры модели"""
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        """Возвращает строковое представление ингредиента."""
        return self.name


class RecipeIngredient(models.Model):
    """Модель для связи между рецептом и ингредиентом."""
    recipe: models.ForeignKey = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_for_recipe',
        verbose_name='Рецепт',)
    ingredient: models.ForeignKey = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='ingtedient_in_recipe')
    quantity: models.FloatField = models.FloatField(
        verbose_name='Количество ингредиента',
        validators=[MinValueValidator(1,
                                      message='Минимальное количество = 1'),])

    def __str__(self):
        """Возвращает строковое представление связи рецепта и ингредиента."""
        return f"{self.quantity} {self.ingredient.unit} of {self.ingredient.name}"


class RecipeTag(models.Model):
    """Модель для связи между рецептом и тэгом."""
    recipe: models.ForeignKey = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт')

    tag: models.ForeignKey = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Теги')

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецепта'


class FavoriteRecipe(models.Model):
    """Модель для избранных рецептов от пользователя."""
    user: models.ForeignKey = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Пользователь')
    recipe: models.ForeignKey = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
        verbose_name='Рецепт')

    class Meta:
        """Мета-класс для уникальности сочетания пользователя и рецепта."""
        unique_together = ('user', 'recipe')
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        """Возвращает строковое представление связи."""
        return f"{self.user.username} -> {self.recipe.title}"


class ShoppingList(models.Model):
    """Модель для списка покупок, где пользователь может добавлять рецепты."""
    user: models.ForeignKey = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='shoppinglist_user',
        verbose_name='Пользователь')
    recipe: models.ForeignKey = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='shoppinglist_recipe',
        verbose_name='Рецепт')

    class Meta:
        """Класс для уникальности сочетания пользователя и рецепта в списке."""
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    # def get_shopping_list(self):
    #     """Получить список ингредиентов для рецептов в списке покупок."""
    #     ingredients = {}
    #     for recipe in self.user.shopping_lists.all():
    #         for recipe_ingredient in recipe.recipe.ingredients.all():
    #             if recipe_ingredient.ingredient not in ingredients:
    #                 ingredients[recipe_ingredient.ingredient] = {
    #                     'quantity': recipe_ingredient.quantity,
    #                     'unit': recipe_ingredient.unit
    #                 }
    #             else:
    #                 ingredients[
    #                     recipe_ingredient.ingredient][
    #                         'quantity'] += recipe_ingredient.quantity
    #     return ingredients

    def __str__(self):
        """Возвращает строковое представление списка покупок."""
        return f"Список покупок для {self.user.username}: {self.recipe.title}"


class Subscription(models.Model):
    """Модель для подписки, которая связывает пользователей друг с другом."""
    author: models.ForeignKey = models.ForeignKey(
        User,
        related_name='subscrib',
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта')
    subscriber: models.ForeignKey = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик')

    class Meta:
        """Мета-параметры модели"""
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f"{self.author} -> {self.subscriber}"
