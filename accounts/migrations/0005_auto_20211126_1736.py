# Generated by Django 3.2.8 on 2021-11-26 17:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20211118_2035'),
    ]

    operations = [
        migrations.RenameField(
            model_name='doubleentry',
            old_name='account_A',
            new_name='account_a',
        ),
        migrations.RenameField(
            model_name='doubleentry',
            old_name='account_B',
            new_name='account_b',
        ),
    ]