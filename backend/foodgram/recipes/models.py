# from django.db import models

# # Create your models here.
from django.db import models
from django.urls import reverse


class Recipe(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='recipes/', blank=True, null=True)
    preparation_time = models.PositiveIntegerField()  # Время приготовления в минутах
    author = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='recipes')
    tags = models.ManyToManyField('Tag', related_name='recipes')
    ingredients = models.ManyToManyField('Ingredient', through='RecipeIngredient')

    def get_short_link(self):
        return reverse('recipe_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title


class Tag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=50)  # Например, граммы, литры, шт.

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField()  # Количество ингредиента
    unit = models.CharField(max_length=50)  # Единица измерения

    def __str__(self):
        return f"{self.quantity} {self.unit} of {self.ingredient.name}"
