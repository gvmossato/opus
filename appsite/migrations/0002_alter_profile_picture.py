# Generated by Django 3.2.9 on 2021-12-14 02:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appsite', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='picture',
            field=models.URLField(default='', max_length=255, null=True),
        ),
    ]
