# Generated by Django 4.2.20 on 2025-03-10 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning_materials', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='materialimage',
            name='image',
            field=models.URLField(max_length=500),
        ),
    ]
