from django.db import models

from tags.constants import (
    MAX_NAME,
    MAX_SLUG,
)


class Tag(models.Model):
    name = models.CharField(
        max_length=MAX_NAME,
        verbose_name='Значение тега'
    )
    slug = models.SlugField(
        max_length=MAX_SLUG,
        verbose_name='Метка'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name
