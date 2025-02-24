"""Модуль кастомной пагинации для API."""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from recipes.constants import DEFAULT_PAGE_SIZE


class CustomPagination(PageNumberPagination):
    """Кастомный пагинатор для управления выводом объектов.

    Позволяет задавать количество объектов на странице через
    параметр запроса `limit`.
    По умолчанию отображает `DEFAULT_PAGE_SIZE` объектов на страницу.
    """

    page_size_query_param = 'limit'
    page_size = DEFAULT_PAGE_SIZE


class UserPagination(PageNumberPagination):
    """Кастомный пагинатор для управления выводом объектов.

    Позволяет задавать количество объектов на странице через
    параметр запроса `limit`.
    По умолчанию отображает `DEFAULT_PAGE_SIZE` объектов на страницу.
    """

    page_size_query_param = 'limit'
    page_size = DEFAULT_PAGE_SIZE

    def get_paginated_response(self, data):
        return Response({
            'results': data
        })
