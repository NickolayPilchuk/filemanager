# Generated by Django 4.2.1 on 2023-08-12 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_alter_files_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='files',
            name='views',
            field=models.IntegerField(default=0),
        ),
    ]
