from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q, F

from users.constants import (
    MAX_USERNAME,
    MAX_EMAIL,
    MAX_FIRST_NAME,
    MAX_LAST_NAME,
)


class MyUser(AbstractUser):
    username = models.CharField(
        max_length=MAX_USERNAME,
        unique=True,
        verbose_name='Имя пользователя',
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message=('Имя пользователя может состоять только '
                         'из букв и символов .@+-')
            )
        ]
    )

    email = models.EmailField(
        max_length=MAX_EMAIL,
        unique=True,
        verbose_name='Адрес электронной почты'
    )

    first_name = models.CharField(
        max_length=MAX_FIRST_NAME,
        verbose_name='Имя'
    )

    last_name = models.CharField(
        max_length=MAX_LAST_NAME,
        verbose_name='Фамилия'
    )

    avatar = models.ImageField(
        upload_to=settings.AVATAR_FOLDER,
        null=True,
        verbose_name='аватар'
    )

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Subscription(models.Model):
    author = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='followers'
    )

    follower = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='followings'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'follower'),
                name='unique_subscription'
            ),
            models.CheckConstraint(
                check=~Q(author=F('follower')),
                name='check_self_subscription',
            )
        ]

    def __str__(self):
        return f'{self.follower.username} follows {self.author.username}'
