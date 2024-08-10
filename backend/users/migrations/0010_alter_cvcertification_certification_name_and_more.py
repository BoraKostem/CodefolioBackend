# Generated by Django 5.0.7 on 2024-08-08 07:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_cvcertification_is_manual_added_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cvcertification',
            name='certification_name',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='cvcertification',
            name='date',
            field=models.CharField(max_length=58),
        ),
        migrations.AlterField(
            model_name='cveducation',
            name='degree',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='cveducation',
            name='end_date',
            field=models.CharField(blank=True, max_length=57, null=True),
        ),
        migrations.AlterField(
            model_name='cveducation',
            name='location',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='cveducation',
            name='school',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='cveducation',
            name='start_date',
            field=models.CharField(max_length=57),
        ),
        migrations.AlterField(
            model_name='cvexperience',
            name='company_name',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='cvexperience',
            name='end_date',
            field=models.CharField(blank=True, max_length=57, null=True),
        ),
        migrations.AlterField(
            model_name='cvexperience',
            name='location',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='cvexperience',
            name='position',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='cvexperience',
            name='start_date',
            field=models.CharField(max_length=57),
        ),
        migrations.AlterField(
            model_name='cvinformation',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cv_information', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='cvproject',
            name='project_name',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='cvprojectlanguage',
            name='language',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='cvskill',
            name='skill',
            field=models.TextField(),
        ),
    ]
