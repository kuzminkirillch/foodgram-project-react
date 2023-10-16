import csv

from django.core.management.base import BaseCommand
from reciepts.models import Ingredient


class Command(BaseCommand):
    """Загрузка данных в БД"""
    def handle(self, *args, **options):
        try:
            load_csv()
            print('ингредиенты загружены')
        except Exception as er:
            print(er)


def load_csv():
    with open('./data/ingredients.csv',
              encoding='utf-8') as csv_file:
        fieldnames = ['name', 'value_unit']
        csv_reader = csv.DictReader(csv_file, fieldnames=fieldnames)
        for row in csv_reader:
            Ingredient.objects.get_or_create(
                name=row['name'],
                value_unit=row['value_unit'])
