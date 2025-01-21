from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Recipe(models.Model):
    """Модель для страницы рецепта пользователя."""
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='recipes/',
                              blank=True,
                              null=True)
    preparation_time = models.PositiveIntegerField()  # минуты
    author = models.ForeignKey('users.User',
                               on_delete=models.CASCADE,
                               related_name='recipes')
    tags = models.ManyToManyField('Tag',
                                  related_name='recipes')
    ingredients = models.ManyToManyField('Ingredient',
                                         through='RecipeIngredient')
    slug = models.SlugField(unique=True,
                            blank=True)

    def get_short_link(self):
        """Возвращает короткую ссылку на рецепт."""
        return reverse('recipe_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        """Переопределенный метод сохранения экземпляра модели."""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        """Возвращает строковое представление рецепта."""
        return self.title


class Tag(models.Model):
    """Модель для тега записи."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        """Возвращает строковое представление тега."""
        return self.name


class Ingredient(models.Model):
    """
    Модель для ингредиента.
    """
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=50)  # Ед: граммы, литры, шт.

    def __str__(self):
        """Возвращает строковое представление ингредиента."""
        return self.name


class RecipeIngredient(models.Model):
    """Модель для связи между рецептом и ингредиентом."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField()  # Количество ингредиента

    def __str__(self):
        """Возвращает строковое представление связи рецепта и ингредиента."""
        return f"{self.quantity} {self.ingredient.unit} of {self.ingredient.name}"
