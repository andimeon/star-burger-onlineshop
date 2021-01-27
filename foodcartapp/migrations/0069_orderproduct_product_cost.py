# Generated by Django 3.0.7 on 2021-01-27 03:46

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0068_auto_20210126_0457'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderproduct',
            name='product_cost',
            field=models.DecimalField(decimal_places=2, max_digits=8, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='стоимость 1ед'),
        ),
    ]
