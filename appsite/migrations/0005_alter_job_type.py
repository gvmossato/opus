# Generated by Django 3.2.9 on 2021-12-08 06:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appsite', '0004_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='type',
            field=models.IntegerField(choices=[(1, 'Convidado'), (2, 'Seguidor'), (3, 'Administrador'), (4, 'Criador')]),
        ),
    ]
