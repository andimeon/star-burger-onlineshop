# Generated by Django 3.0.7 on 2020-10-18 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0047_auto_20201018_1422'),
    ]

    operations = [
        migrations.AddField(
            model_name='banner',
            name='banner_name',
            field=models.CharField(default='somename', max_length=200, verbose_name='название'),
            preserve_default=False,
        ),
    ]