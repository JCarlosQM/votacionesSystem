# Generated by Django 5.2 on 2025-05-07 07:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_votante_created_at'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Integrante',
        ),
    ]
