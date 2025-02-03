import django_filters
from recipes.models import Ingredient

class IngredientFilter(django_filters.FilterSet):
    # Устанавливаем поиск по подстроке, игнорируя регистр
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ['name']
