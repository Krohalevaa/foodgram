"""Команда Django для загрузки ингредиентов из CSV-файла в базу данных."""

import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from recipes.models import Ingredient


class Command(BaseCommand):
    """Класс команды для импорта ингредиентов из CSV-файла.

    Команда загружает данные в модель `Ingredient` из CSV-файла без заголовков.
    Формат CSV-файла: каждая строка содержит название ингредиента
    и его единицу измерения.

    Атрибут:
        help (str): Описание команды для `manage.py help`.
    """

    help = "Загружает ингредиенты из CSV файла (без заголовков)"

    def add_arguments(self, parser):
        """
        Добавляет аргументы командной строки.

        Аргументы:
            parser (ArgumentParser): Объект парсера аргументов.
        """
        parser.add_argument(
            '--path',
            type=str,
            help="/data/ingredients.csv/",
            default=os.path.join(settings.BASE_DIR, 'data', 'ingredients.csv')
        )

    def handle(self, *args, **options):
        """Основной метод выполнения команды.

        Читает CSV-файл, парсит данные и добавляет новые ингредиенты
        в базу данных.

        Аргументы:
            *args: Позиционные аргументы (не используются).
            **options: Словарь аргументов командной строки.
        """
        csv_path = options['path']
        self.stdout.write(f"Чтение файла: {csv_path}")

        try:
            with open(csv_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                count = 0
                for row in reader:
                    if not row or len(row) < 2:
                        self.stdout.write(
                            "Пропущена пустая или некорректная строка.")
                        continue
                    name = row[0].strip()
                    unit = row[1].strip()
                    if not name:
                        self.stdout.write(
                            "Строка пропущена, т.к. имя не указано.")
                        continue
                    ingredient, created = Ingredient.objects.get_or_create(
                        name=name,
                        defaults={'unit': unit}
                    )
                    if created:
                        count += 1
                self.stdout.write(self.style.SUCCESS(
                    f"Загружено {count} ингредиентов."))
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"Файл не найден: {csv_path}"))
