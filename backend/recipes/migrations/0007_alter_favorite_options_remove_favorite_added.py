# Generated by Django 4.2 on 2023-09-10 14:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_alter_recipeingredient_ingredient_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favorite',
            options={'verbose_name': 'Favorite'},
        ),
        migrations.RemoveField(
            model_name='favorite',
            name='added',
        ),
    ]