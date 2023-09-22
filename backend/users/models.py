from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint


class CustomUser(AbstractUser):
    email = models.EmailField('email', null=False, unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        ordering = ['id']

    def __str__(self):
        return f'User {self.email}'


User = CustomUser


class Follow(models.Model):
    following = models.ForeignKey(User, on_delete=models.CASCADE,
                                  verbose_name='Subscription',
                                  related_name='following')
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Подписчик',
                             related_name='follower')

    class Meta:
        verbose_name = 'Subscription'
        constraints = [
            UniqueConstraint(fields=['following', 'user'],
                             name='follow_unique')
        ]

    def __str__(self):
        return f"{self.user} follows {self.following}"
