"""Конфигурация приложения API в Django."""

from django.apps import AppConfig


class ApiConfig(AppConfig):
    """
    Класс конфигурации приложения 'api'.

    Определяет настройки для приложения API.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
