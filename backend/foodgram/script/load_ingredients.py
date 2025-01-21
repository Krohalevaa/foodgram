import csv
from recipes.models import Ingredient

def load_ingredients():
    with open('_data_/ingredients.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = row['name']
            unit = row['unit']
            ingredient, created = Ingredient.objects.get_or_create(name=name, unit=unit)
            if created:
                print(f"Ингредиент {name} ({unit}) успешно добавлен.")
            else:
                print(f"Ингредиент {name} ({unit}) уже существует.")
