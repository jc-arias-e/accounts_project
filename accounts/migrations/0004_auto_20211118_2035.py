# Generated by Django 3.2.8 on 2021-11-18 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20211025_2050'),
    ]

    operations = [
        migrations.CreateModel(
            name='Parameters',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
            ],
        ),
        migrations.AlterModelOptions(
            name='alias',
            options={'verbose_name_plural': 'aliases'},
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name_plural': 'categories'},
        ),
        migrations.AlterModelOptions(
            name='subcategory',
            options={'verbose_name_plural': 'subcategories'},
        ),
    ]
