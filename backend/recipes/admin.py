from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from recipes.models import (Ingredient, Recipe, Tag,
                            Favorite, ShoppingCart, RecipeIngredient)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Configuration for the Tag model in the admin panel."""
    list_display = ('name', 'slug', 'color',)
    list_editable = ('color',)
    list_filter = ('name', 'slug',)
    search_fields = ('name',)
    empty_value_display = _('empty')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Configuration for the Ingredient model in the admin panel."""
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)
    search_fields = ('name',)
    empty_value_display = _('empty')


class RecipeIngredientInline(admin.TabularInline):
    """Inline class for recipe ingredients."""
    model = Recipe.ingredients.through
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Configuration for the Recipe model in the admin panel."""
    list_display = ('name', 'author',)
    list_filter = ('author', 'name', 'tags')
    search_fields = ('name',)
    filter_horizontal = ('tags',)
    inlines = (RecipeIngredientInline,)
    empty_value_display = _('empty')
    fields = (
        'name',
        'author',
        'pub_date',
        'image',
        'cooking_time',
        'text',
        'tags',
    )


admin.site.register(Favorite)
admin.site.register(RecipeIngredient)
admin.site.register(ShoppingCart)


admin.site.site_title = _('Foodgram admin-zone')
admin.site.site_header = _('Foodgram admin-zone')
