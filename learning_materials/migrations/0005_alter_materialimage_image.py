# learning_materials/migrations/0005_alter_materialimage_image.py

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('learning_materials', '0004_alter_materialimage_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='materialimage',
            name='image',
            field=models.URLField(max_length=500),
        ),
    ]