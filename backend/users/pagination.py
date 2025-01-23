from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Кастомная пагинация с размером страницы 6 элементов."""
    page_size = 6
