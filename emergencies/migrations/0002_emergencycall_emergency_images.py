# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emergencies', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='emergencycall',
            name='emergency_images',
            field=models.JSONField(blank=True, default=list, help_text='List of image URLs uploaded with the emergency'),
        ),
    ]
