from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, validate_slug
from django.db.models import (Model, CharField, SlugField, UniqueConstraint,
                              DateTimeField, ImageField, TextField,
                              PositiveSmallIntegerField, ManyToManyField,
                              ForeignKey, CASCADE)
from django.utils import timezone

from api.validators import (validate_hex)

User = get_user_model()


class Tag(Model):
    name = CharField(
        verbose_name='Tag',
        max_length=150,
        unique=True,
    )
    color = CharField(
        verbose_name='Color',
        max_length=7,
        unique=True,
        validators=[validate_hex],
    )
    slug = SlugField(
        verbose_name='Tag slug',
        unique=True,
        max_length=50,
        validators=[validate_slug],
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name


class Ingredient(Model):
    name = CharField(
        verbose_name='Ingredient',
        max_length=150,
    )
    measurement_unit = CharField(
        verbose_name='Measurement_unit',
        max_length=30,
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit'
            )
        ]
        ordering = ['name']
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipe(Model):
    name = CharField(
        verbose_name='name',
        max_length=250,
    )
    pub_date = DateTimeField(
        verbose_name='publication date',
        default=timezone.now,
        db_index=True
    )
    image = ImageField(
        verbose_name='image',
        upload_to='media/',
    )
    text = TextField(
        verbose_name='recipe text',
    )
    cooking_time = PositiveSmallIntegerField(
        verbose_name='cooking time (minutes)',
        validators=[
            MinValueValidator(
                1, message='Minimum cooking time 1 minute'
            )
        ]
    )
    ingredients = ManyToManyField(
        Ingredient,
        verbose_name='ingredients',
        blank=True,
        through='RecipeIngredient',
        related_name='ingredients',
    )
    tags = ManyToManyField(
        Tag,
        verbose_name='tags',
        blank=True,
        related_name='tags',
    )
    author = ForeignKey(
        User,
        verbose_name='author',
        on_delete=CASCADE,
        related_name='recipes',
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'recipe'
        verbose_name_plural = 'recipes'

    def __str__(self):
        return self.name


class Favorite(Model):
    user = ForeignKey(
        User, related_name='favorites',
        on_delete=CASCADE
    )
    recipe = ForeignKey(
        Recipe, related_name='favorites',
        on_delete=CASCADE
    )

    class Meta:
        verbose_name = 'Favorite'
        constraints = [
            UniqueConstraint(fields=['recipe', 'user'], name='favorite_unique')
            ]

    def __str__(self):
        return f"{self.user} has favorites: {self.recipe.name}"


class ShoppingList(Model):
    user = ForeignKey(
        User, on_delete=CASCADE,
        related_name='user_shopping_list',
        verbose_name='Пользоавтель'
    )
    recipe = ForeignKey(
        Recipe, on_delete=CASCADE,
        related_name='purchases',
        verbose_name='Покупка'
    )
    added = DateTimeField(
        auto_now_add=True, verbose_name='Дата добавления в список покупок'
    )

    class Meta:
        verbose_name = 'Sopping list'
        constraints = [
            UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_recipe_cart'
            )
        ]

    def __str__(self):
        return f'In {self.user} shopping list: {self.recipe}'


class RecipeIngredient(Model):
    recipe = ForeignKey(
        Recipe,
        verbose_name='recipe',
        on_delete=CASCADE,
        related_name='recipes_ingredients_list'
    )
    ingredient = ForeignKey(
        Ingredient,
        verbose_name='ingredient',
        on_delete=CASCADE,
        related_name='ingredients_in_recipe'
    )
    amount = PositiveSmallIntegerField(
        verbose_name='amount',
        validators=[
            MinValueValidator(
                1, message='The minimum ingredientes in a recipe is 1'
            )
        ]
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]
        verbose_name = 'recipe ingredient'
        verbose_name_plural = 'recipe ingredients'

    def __str__(self):
        return f'{self.ingredient} - {self.amount}'
