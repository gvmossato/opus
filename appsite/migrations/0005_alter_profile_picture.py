# Generated by Django 3.2.9 on 2021-12-14 02:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appsite', '0004_alter_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='picture',
            field=models.URLField(default='https://avataaars.io/?avatarStyle=Transparent&accessoriesType=Round&hairColorCode=#4A322B&hairColor=SilverGray&clotheColor=Pink&clotheColorCode=#3C4F5C&facialHairType=BeardMagestic&clotheType=BlazerSweater&eyeType=Default&eyebrowType=UpDown&mouthType=Serious&skinColor=Black&topType=LongHairCurly', max_length=510, null=True),
        ),
    ]
