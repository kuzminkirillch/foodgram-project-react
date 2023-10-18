from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()


class Ingredient(models.Model):
    """Ингридиенты для рецептов."""

    name = models.CharField(verbose_name='Название', max_length=100,
                            db_index=True)

    value_unit = models.CharField(verbose_name='Величина', max_length=100)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} ({self.value_unit})'


class Tags(models.Model):
    """Тэги для рецептов с предустановленным выбором."""

    name = models.CharField(verbose_name='Название', unique=True,
                            max_length=100)
    slug = models.SlugField(verbose_name='Слаг', unique=True, max_length=30)
    color = models.CharField(verbose_name='Цвет', unique=True, max_length=7)

    class Meta:
        unique_together = ("name", "color", "slug")
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Reciept(models.Model):
    """
    Модель для рецептов.
    """
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор рецепта',
                               related_name='reciept')
    name = models.CharField(verbose_name='Название', max_length=50)
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='Routing',
                                         verbose_name='Ингредиенты',
                                         related_name='reciepts')
    image = models.ImageField(upload_to='reciepts/images/')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[MinValueValidator(1, 'Обозначте время приготовления')]
    )
    tags = models.ManyToManyField(Tags,
                                  verbose_name='Тэги',
                                  related_name='reciept')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-id',)

    def __str__(self):
        return self.name


class Routing(models.Model):
    """
    Технологическая карта создания рецепта и добавления ингридиентов
    """
    reciept = models.ForeignKey(Reciept, on_delete=models.CASCADE,
                                related_name='ingredient_list')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(1, 'Обозначте ингридиенты для рецепта')]
    )

    def __str__(self):
        return f'Ингридиент: {self.ingredient.name}, количество: {self.amount}'

    class Meta:
        verbose_name = 'Технологическая карта'


class Favorite(models.Model):
    """
    Избранные рецепты.
    """
    reciept = models.ForeignKey(
        Reciept,
        on_delete=models.CASCADE,
        verbose_name='Рецепт - избранное',
        related_name='favorite'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorite'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            UniqueConstraint(
                fields=('reciept', 'author'),
                name='unique_author_favorite'
            )
        ]

    def __str__(self):
        return f'{self.reciept} добавлен в избранное'


class ShoppingList(models.Model):
    """
    Список покупок. Можно выгрузить в формате txt.
    """
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='shopping',
                               verbose_name='Пользователь')
    reciept = models.ForeignKey(Reciept, on_delete=models.CASCADE,
                                related_name='shopping', verbose_name='Рецепт')

    class Meta:
        verbose_name = 'Корзина'
        constraints = [UniqueConstraint(fields=['author', 'reciept'],
                                        name='unique_shopping_list')]

    def __str__(self):
        return f'Продукты для {self.reciept} добавлены в корзину.'
