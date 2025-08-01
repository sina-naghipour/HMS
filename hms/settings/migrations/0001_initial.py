# Generated by Django 5.0.7 on 2025-07-27 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HotelSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site_name', models.CharField(default='Hotel Management System', max_length=100)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='settings/')),
                ('address', models.CharField(blank=True, max_length=255)),
                ('phone', models.CharField(blank=True, max_length=40)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('tax_rate', models.DecimalField(decimal_places=2, default=9.0, max_digits=5)),
                ('currency', models.CharField(default='IRR', max_length=10)),
            ],
        ),
    ]
