# Generated by Django 5.0.7 on 2025-07-27 08:43

import django.core.validators
import django.db.models.deletion
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Amenity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Amenity Name')),
                ('icon', models.CharField(blank=True, help_text='Use Tabler Icons class names', max_length=50, verbose_name='Icon')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('category', models.CharField(choices=[('basic', 'Basic'), ('entertainment', 'Entertainment'), ('business', 'Business'), ('luxury', 'Luxury'), ('accessibility', 'Accessibility')], default='basic', max_length=50, verbose_name='Category')),
                ('is_chargeable', models.BooleanField(default=False, verbose_name='Chargeable')),
                ('extra_charge', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=8, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='Extra Charge')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
            ],
            options={
                'verbose_name': 'Amenity',
                'verbose_name_plural': 'Amenities',
                'ordering': ['category', 'name'],
                'indexes': [models.Index(fields=['category'], name='rooms_ameni_categor_59b56f_idx'), models.Index(fields=['is_active'], name='rooms_ameni_is_acti_b0799a_idx')],
            },
        ),
        migrations.CreateModel(
            name='RoomType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Room Type')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('base_price', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='Base Price')),
                ('max_occupancy', models.PositiveSmallIntegerField(default=2, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)], verbose_name='Maximum Occupancy')),
                ('size_sqm', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Size (Square Meters)')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('default_amenities', models.ManyToManyField(blank=True, related_name='room_types', to='rooms.amenity', verbose_name='Default Amenities')),
            ],
            options={
                'verbose_name': 'Room Type',
                'verbose_name_plural': 'Room Types',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(db_index=True, max_length=10, unique=True, verbose_name='Room Number')),
                ('floor', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(50)], verbose_name='Floor')),
                ('capacity', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)], verbose_name='Capacity')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='Nightly Price')),
                ('status', models.CharField(choices=[('available', 'Available'), ('occupied', 'Occupied'), ('maintenance', 'Under Maintenance'), ('reserved', 'Reserved'), ('out_of_order', 'Out of Order')], db_index=True, default='available', max_length=20, verbose_name='Status')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('size_sqm', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Size (Square Meters)')),
                ('view_type', models.CharField(blank=True, choices=[('city', 'City View'), ('ocean', 'Ocean View'), ('mountain', 'Mountain View'), ('garden', 'Garden View'), ('pool', 'Pool View'), ('courtyard', 'Courtyard View')], max_length=50, verbose_name='View Type')),
                ('balcony', models.BooleanField(default=False, verbose_name='Has Balcony')),
                ('smoking_allowed', models.BooleanField(default=False, verbose_name='Smoking Allowed')),
                ('last_maintenance', models.DateField(blank=True, null=True, verbose_name='Last Maintenance')),
                ('next_maintenance', models.DateField(blank=True, null=True, verbose_name='Next Maintenance')),
                ('maintenance_notes', models.TextField(blank=True, verbose_name='Maintenance Notes')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('amenities', models.ManyToManyField(blank=True, to='rooms.amenity', verbose_name='Amenities')),
                ('room_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rooms', to='rooms.roomtype', verbose_name='Room Type')),
            ],
            options={
                'verbose_name': 'Room',
                'verbose_name_plural': 'Rooms',
                'ordering': ['floor', 'number'],
            },
        ),
        migrations.AddIndex(
            model_name='roomtype',
            index=models.Index(fields=['name'], name='rooms_roomt_name_fb1a0c_idx'),
        ),
        migrations.AddIndex(
            model_name='roomtype',
            index=models.Index(fields=['is_active'], name='rooms_roomt_is_acti_76aa4b_idx'),
        ),
        migrations.AddIndex(
            model_name='room',
            index=models.Index(fields=['floor', 'number'], name='rooms_room_floor_cad89e_idx'),
        ),
        migrations.AddIndex(
            model_name='room',
            index=models.Index(fields=['status', 'is_active'], name='rooms_room_status_09b4a0_idx'),
        ),
        migrations.AddIndex(
            model_name='room',
            index=models.Index(fields=['room_type', 'status'], name='rooms_room_room_ty_a51164_idx'),
        ),
        migrations.AddIndex(
            model_name='room',
            index=models.Index(fields=['capacity'], name='rooms_room_capacit_a254a2_idx'),
        ),
    ]
