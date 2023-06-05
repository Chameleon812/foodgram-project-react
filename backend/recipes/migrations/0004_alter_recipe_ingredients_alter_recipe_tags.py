# Generated by Django 4.2 on 2023-06-04 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_alter_recipe_ingredients_alter_recipe_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(blank=True, related_name='ingredients', through='recipes.RecipeIngredient', to='recipes.ingredient', verbose_name='ingredients'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='tags', to='recipes.tag', verbose_name='tags'),
        ),
    ]