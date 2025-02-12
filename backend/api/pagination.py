"""Модуль кастомной пагинации для API."""

from rest_framework.pagination import PageNumberPagination

DEFAULT_PAGE_SIZE = 6


class CustomPagination(PageNumberPagination):
    """Кастомный пагинатор для управления выводом объектов.

    Позволяет задавать количество объектов на странице через
    параметр запроса `limit`.
    По умолчанию отображает `DEFAULT_PAGE_SIZE` объектов на страницу.
    """

    page_size_query_param = 'limit'
    page_size = DEFAULT_PAGE_SIZE
