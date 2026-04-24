from django.db import models

from ingredients.constants import (
    MAX_NAME,
    MAX_UNIT
)


class Ingredient(models.Model):
    class MeasurementUnit(models.TextChoices):
        GRAM = 'GM', 'г'
        KILOGRAM = 'KG', 'кг'
        MILLILITER = 'ML', 'мл'
        LITER = 'LT', 'л'
        ITEM = 'IT', 'шт.'
        TBSPOON = 'TS', 'ст. л.'
        TEASPOON = 'TE', 'ч. л.'
        LOAF = 'LF', 'батон'
        DROP = 'DR', 'капля'
        JAR = 'JR', 'банка'
        HANDFUL = 'HF', 'горсть'
        TWIG = 'TW', 'веточка'
        PINCH = 'PN', 'щепотка'
        GLASS = 'GL', 'стакан'
        PIECE = 'PC', 'кусок'
        TASTE = 'TT', 'по вкусу'

    name = models.CharField(
        max_length=MAX_NAME,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=MAX_UNIT,
        choices=MeasurementUnit.choices,
        default=MeasurementUnit.GRAM,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name
