# Generated by Django 3.2.9 on 2021-12-14 20:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source_id', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active_invite', models.BooleanField()),
                ('type', models.IntegerField(choices=[(1, 'Convidado'), (2, 'Seguidor'), (3, 'Administrador'), (4, 'Criador')])),
            ],
        ),
        migrations.CreateModel(
            name='List',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('symbol', models.CharField(max_length=2)),
                ('description', models.TextField(max_length=255, null=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('color', models.CharField(default='#F20574', max_length=7)),
                ('picture', models.URLField(default='https://images.unsplash.com/photo-1515847049296-a281d6401047?w=1920', max_length=510)),
                ('user', models.ManyToManyField(through='appsite.Job', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_id', models.IntegerField(blank=True, null=True)),
                ('name', models.CharField(max_length=255)),
                ('done', models.BooleanField(default=False)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('due_date', models.CharField(max_length=10)),
                ('list', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appsite.list')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('value', models.CharField(max_length=255)),
                ('list', models.ManyToManyField(through='appsite.Follow', to='appsite.List')),
                ('task', models.ManyToManyField(to='appsite.Task')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('picture', models.URLField(default='', max_length=510, null=True)),
                ('description', models.TextField(default='Adicione uma descrição pra completar seu perfil.', max_length=255, null=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='job',
            name='list',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appsite.list'),
        ),
        migrations.AddField(
            model_name='job',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='follow',
            name='list',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appsite.list'),
        ),
        migrations.AddField(
            model_name='follow',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appsite.tag'),
        ),
    ]
