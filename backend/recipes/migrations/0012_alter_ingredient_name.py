# Generated by Django 4.2 on 2023-10-28 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0011_alter_recipe_ingredients_alter_recipe_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(db_index=True, max_length=150, verbose_name='Ingredient'),
        ),
    ]
