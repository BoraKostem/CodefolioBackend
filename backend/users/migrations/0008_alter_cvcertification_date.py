# Generated by Django 5.0.6 on 2024-07-15 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_alter_cvskill_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cvcertification',
            name='date',
            field=models.CharField(max_length=18),
        ),
    ]