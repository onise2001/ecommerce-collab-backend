# Generated by Django 5.0.7 on 2024-09-01 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce_api', '0006_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('name', models.CharField(max_length=255)),
            ],
        ),
    ]
