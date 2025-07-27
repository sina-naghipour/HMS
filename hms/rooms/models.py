from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from decimal import Decimal

class RoomType(models.Model):
    name = models.CharField(_('Room Type'), max_length=100, unique=True)
    description = models.TextField(_('Description'), blank=True)
    base_price = models.DecimalField(
        _('Base Price'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    max_occupancy = models.PositiveSmallIntegerField(
        _('Maximum Occupancy'),
        default=2,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    size_sqm = models.PositiveIntegerField(
        _('Size (Square Meters)'),
        null=True,
        blank=True,
        validators=[MinValueValidator(1)]
    )
    default_amenities = models.ManyToManyField(
        'Amenity',
        verbose_name=_('Default Amenities'),
        blank=True,
        related_name='room_types'
    )
    
    # Audit fields
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    is_active = models.BooleanField(_('Active'), default=True)
    
    class Meta:
        verbose_name = _('Room Type')
        verbose_name_plural = _('Room Types')
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name

    @property
    def min_price(self):
        """Get minimum room price or fallback to base_price"""
        min_price = self.rooms.filter(is_active=True).aggregate(
            min_price=models.Min('price')
        )['min_price']
        return min_price or self.base_price

    @property
    def max_price(self):
        """Get maximum room price or fallback to base_price"""
        max_price = self.rooms.filter(is_active=True).aggregate(
            max_price=models.Max('price')
        )['max_price']
        return max_price or self.base_price

    @property
    def room_count(self):
        """Get count of active rooms with this type"""
        return self.rooms.filter(is_active=True).count()
    
    @property
    def available_room_count(self):
        """Get count of available rooms"""
        return self.rooms.filter(status='available', is_active=True).count()

class Amenity(models.Model):
    name = models.CharField(_('Amenity Name'), max_length=100, unique=True)
    icon = models.CharField(
        _('Icon'), 
        max_length=50,
        blank=True,
        help_text=_("Use Tabler Icons class names")
    )
    description = models.TextField(_('Description'), blank=True)
    category = models.CharField(
        _('Category'),
        max_length=50,
        choices=[
            ('basic', _('Basic')),
            ('entertainment', _('Entertainment')),
            ('business', _('Business')),
            ('luxury', _('Luxury')),
            ('accessibility', _('Accessibility')),
        ],
        default='basic'
    )
    is_chargeable = models.BooleanField(_('Chargeable'), default=False)
    extra_charge = models.DecimalField(
        _('Extra Charge'),
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    is_active = models.BooleanField(_('Active'), default=True)
    
    class Meta:
        verbose_name = _('Amenity')
        verbose_name_plural = _('Amenities')
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name

class Room(models.Model):
    class StatusChoices(models.TextChoices):
        AVAILABLE = 'available', _('Available')
        OCCUPIED = 'occupied', _('Occupied')
        MAINTENANCE = 'maintenance', _('Under Maintenance')
        RESERVED = 'reserved', _('Reserved')
        OUT_OF_ORDER = 'out_of_order', _('Out of Order')
    
    number = models.CharField(_('Room Number'), max_length=10, unique=True, db_index=True)
    room_type = models.ForeignKey(
        RoomType,
        on_delete=models.PROTECT,
        verbose_name=_('Room Type'),
        related_name='rooms'
    )
    floor = models.PositiveSmallIntegerField(
        _('Floor'),
        validators=[MinValueValidator(1), MaxValueValidator(50)]
    )
    capacity = models.PositiveSmallIntegerField(
        _('Capacity'),
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    price = models.DecimalField(
        _('Nightly Price'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.AVAILABLE,
        db_index=True
    )
    amenities = models.ManyToManyField(
        Amenity,
        verbose_name=_('Amenities'),
        blank=True
    )
    description = models.TextField(_('Description'), blank=True)
    
    # Additional useful fields
    size_sqm = models.PositiveIntegerField(
        _('Size (Square Meters)'),
        null=True,
        blank=True,
        validators=[MinValueValidator(1)]
    )
    view_type = models.CharField(
        _('View Type'),
        max_length=50,
        choices=[
            ('city', _('City View')),
            ('ocean', _('Ocean View')),
            ('mountain', _('Mountain View')),
            ('garden', _('Garden View')),
            ('pool', _('Pool View')),
            ('courtyard', _('Courtyard View')),
        ],
        blank=True
    )
    balcony = models.BooleanField(_('Has Balcony'), default=False)
    smoking_allowed = models.BooleanField(_('Smoking Allowed'), default=False)
    
    # Maintenance fields
    last_maintenance = models.DateField(_('Last Maintenance'), null=True, blank=True)
    next_maintenance = models.DateField(_('Next Maintenance'), null=True, blank=True)
    maintenance_notes = models.TextField(_('Maintenance Notes'), blank=True)
    
    # Audit fields
    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Room')
        verbose_name_plural = _('Rooms')
        ordering = ['floor', 'number']
        indexes = [
            models.Index(fields=['floor', 'number']),
            models.Index(fields=['status', 'is_active']),
            models.Index(fields=['room_type', 'status']),
            models.Index(fields=['capacity']),
        ]
    
    def __str__(self):
        return f"Room {self.number} (Floor {self.floor})"
    
    def clean(self):
        """Custom validation"""
        super().clean()
        
        if self.capacity > self.room_type.max_occupancy:
            raise ValidationError(
                _('Room capacity cannot exceed room type maximum occupancy')
            )
    
    def get_final_price(self):
        """Calculate final price including amenity charges"""
        base_price = self.price
        amenity_charges = self.amenities.filter(
            is_chargeable=True
        ).aggregate(
            total_charges=models.Sum('extra_charge')
        )['total_charges'] or Decimal('0.00')
        
        return base_price + amenity_charges
    
    @property
    def is_available(self):
        """Check if room is available for booking"""
        return self.status == self.StatusChoices.AVAILABLE and self.is_active
    
    def get_current_booking(self):
        """Get current active booking for this room"""
        from django.utils import timezone
        today = timezone.now().date()
        
        return self.bookings.filter(
            check_in__lte=today,
            check_out__gt=today,
            status__in=['reserved', 'checked_in'],
            is_trash=False
        ).first()