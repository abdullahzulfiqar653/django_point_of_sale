# Generated by Django 4.1.5 on 2024-01-24 06:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='expire_date',
            field=models.DateField(null=True),
        ),
    ]
