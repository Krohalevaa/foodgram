"""Модуль моделей для работы с пользователями."""

from django.contrib.auth.models import AbstractUser, Permission
from django.db import models
from recipes.constants import MAX_LENGHT, MAX_LENGHT_EAMAIL


class User(AbstractUser):
    """
    Модель пользователя, наследующая от AbstractUser.

    Эта модель используется для расширения стандартной модели
    пользователя Django.
    Она добавляет дополнительные поля для электронной почты,
    никнейма, аватара пользователя и групп.
    Также переопределяет поле USERNAME_FIELD, устанавливая email
    как уникальный идентификатор пользователя.
    """

    email = models.EmailField(
        unique=True,
        max_length=MAX_LENGHT_EAMAIL,
        verbose_name='Электронная почта')
    username = models.CharField(
        unique=True,
        max_length=MAX_LENGHT,
        verbose_name='Никнейм пользователя')
    first_name = models.CharField(
        max_length=MAX_LENGHT,
        verbose_name='Имя пользователя')
    last_name = models.CharField(
        max_length=MAX_LENGHT,
        verbose_name='Фамилия пользователя')
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Аватар пользователя')
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_users_permissions',
        blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        """
        Метаданные для модели пользователя.

        Устанавливает отображение в административной панели
        Django и сортировку по id.
        """

        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        """
        Строковое представление объекта пользователя.

        Возвращает никнейм пользователя.
        """
        return self.username
