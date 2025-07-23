from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

class RoomType(models.Model):
    name = models.CharField(_('Room Type'), max_length=100)
    description = models.TextField(_('Description'), blank=True)
    base_price = models.PositiveIntegerField(_('Base Price'), default=0)
    default_amenities = models.ManyToManyField(
        'Amenity',
        verbose_name=_('Default Amenities'),
        blank=True,
        related_name='room_types'
    )
    
    class Meta:
        verbose_name = _('Room Type')
        verbose_name_plural = _('Room Types')
    
    def __str__(self):
        return self.name

    @property
    def min_price(self):
        """Get minimum room price or fallback to base_price"""
        return self.rooms.aggregate(min_price=models.Min('price'))['min_price'] or self.base_price

    @property
    def max_price(self):
        """Get maximum room price or fallback to base_price"""
        return self.rooms.aggregate(max_price=models.Max('price'))['max_price'] or self.base_price

    @property
    def room_count(self):
        """Get count of rooms with this type"""
        return self.rooms.count()

class Amenity(models.Model):
    name = models.CharField(_('Amenity Name'), max_length=100)
    icon = models.CharField(_('Icon'), max_length=50, 
                          help_text="Use Tabler Icons class names")
    
    class Meta:
        verbose_name = _('Amenity')
        verbose_name_plural = _('Amenities')
    
    def __str__(self):
        return self.name

class Room(models.Model):
    class StatusChoices(models.TextChoices):
        AVAILABLE = 'available', _('Available')
        OCCUPIED = 'occupied', _('Occupied')
        MAINTENANCE = 'maintenance', _('Under Maintenance')
        RESERVED = 'reserved', _('Reserved')
    
    number = models.CharField(_('Room Number'), max_length=10, unique=True)
    room_type = models.ForeignKey(
        RoomType,
        on_delete=models.PROTECT,
        verbose_name=_('Room Type'),
        related_name='rooms'
    )
    floor = models.PositiveSmallIntegerField(
        _('Floor'),
        validators=[MinValueValidator(1), MaxValueValidator(20)]
    )
    capacity = models.PositiveSmallIntegerField(
        _('Capacity'),
        validators=[MinValueValidator(1), MaxValueValidator(6)]
    )
    price = models.PositiveIntegerField(_('Nightly Price'))
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.AVAILABLE
    )
    amenities = models.ManyToManyField(
        Amenity,
        verbose_name=_('Amenities'),
        blank=True
    )
    description = models.TextField(_('Description'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Room')
        verbose_name_plural = _('Rooms')
        ordering = ['floor', 'number']
    
    def __str__(self):
        return f"Room {self.number} (Floor {self.floor})"
    
    def get_final_price(self):
        """Calculate final price including any dynamic pricing"""
        return self.price