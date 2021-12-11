# Generated by Django 3.2.9 on 2021-12-11 04:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appsite', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='description',
            field=models.TextField(default='Adicione uma descrição pra completar seu perfil', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='picture',
            field=models.URLField(default='https://avataaars.io/?avatarStyle=Circle&topType=LongHairStraight&accessoriesType=Blank&hairColor=BrownDark&facialHairType=Blank&clotheType=BlazerShirt&eyeType=Default&eyebrowType=Default&mouthType=Default&skinColor=Light', max_length=255, null=True),
        ),
    ]