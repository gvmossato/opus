# Generated by Django 3.2.9 on 2021-12-09 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appsite', '0002_auto_20211209_0856'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='tag',
        ),
        migrations.AddField(
            model_name='tag',
            name='task',
            field=models.ManyToManyField(to='appsite.Task'),
        ),
    ]
