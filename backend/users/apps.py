"""Модуль конфигурации приложения."""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    Конфигурация приложения 'users'.

    Этот класс описывает настройки и конфигурацию для приложения пользователей.
    Он наследует от AppConfig и указывает на название приложения
    и автоматическое создание полей для моделей.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
