# Generated by Django 3.2.9 on 2021-12-09 07:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appsite', '0005_alter_job_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='task',
            old_name='origin',
            new_name='original_id',
        ),
        migrations.RemoveField(
            model_name='tag',
            name='user',
        ),
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source_id', models.IntegerField()),
                ('list', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appsite.list')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appsite.tag')),
            ],
        ),
        migrations.AddField(
            model_name='tag',
            name='list',
            field=models.ManyToManyField(through='appsite.Follow', to='appsite.List'),
        ),
    ]
