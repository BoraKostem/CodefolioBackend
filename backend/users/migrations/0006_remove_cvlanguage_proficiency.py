# Generated by Django 5.0.6 on 2024-07-09 22:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_cvcertification_cveducation_cvexperience_cvskill'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cvlanguage',
            name='proficiency',
        ),
    ]