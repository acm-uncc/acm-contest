# Generated by Django 2.1.7 on 2019-03-07 04:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jam', '0005_auto_20190306_2215'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='part',
            name='problem',
        ),
        migrations.AddField(
            model_name='problem',
            name='solution',
            field=models.TextField(default='', max_length=10000),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Part',
        ),
    ]
