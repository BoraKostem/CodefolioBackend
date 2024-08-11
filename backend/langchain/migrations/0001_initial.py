# Generated by Django 5.0.7 on 2024-08-10 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.CharField(max_length=255, unique=True)),
                ('user_id', models.CharField(max_length=255)),
                ('user_name', models.CharField(max_length=255, null=True)),
                ('last_activity', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
