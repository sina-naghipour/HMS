from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

class Booking(models.Model):
    STATUS_CHOICES = [
        ('reserved', _('Reserved')),
        ('confirmed', _('Confirmed')),
        ('checked_in', _('Checked In')),
        ('checked_out', _('Checked Out')),
        ('cancelled', _('Cancelled')),
        ('no_show', _('No Show')),
    ]

    # Core booking information
    booking_reference = models.CharField(
        _('Booking Reference'),
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        db_index=True
    )
    room = models.ForeignKey(
        'rooms.Room',
        on_delete=models.PROTECT,
        verbose_name=_('Room'),
        related_name='bookings'
    )
    check_in = models.DateField(_('Check In Date'), db_index=True)
    check_out = models.DateField(_('Check Out Date'), db_index=True)
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='reserved',
        db_index=True
    )
    
    # Guest and staff information
    primary_guest = models.ForeignKey(
        'guests.Guest',
        on_delete=models.PROTECT,
        related_name='primary_bookings',
        verbose_name=_('Primary Guest')
    )
    assigned_staff = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.PROTECT,
        related_name='staff_bookings',
        verbose_name=_('Assigned Staff')
    )
    
    # Booking details
    adults = models.PositiveSmallIntegerField(_('Number of Adults'), default=1)
    children = models.PositiveSmallIntegerField(_('Number of Children'), default=0)
    special_requests = models.TextField(_('Special Requests'), blank=True)
    
    # Pricing information
    room_rate = models.DecimalField(
        _('Room Rate per Night'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('100.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    total_amount = models.DecimalField(
        _('Total Amount'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    discount_amount = models.DecimalField(
        _('Discount Amount'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    tax_amount = models.DecimalField(
        _('Tax Amount'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Payment information
    payment_status = models.CharField(
        _('Payment Status'),
        max_length=20,
        choices=[
            ('pending', _('Pending')),
            ('partial', _('Partially Paid')),
            ('paid', _('Fully Paid')),
            ('refunded', _('Refunded')),
        ],
        default='pending'
    )
    advance_payment = models.DecimalField(
        _('Advance Payment'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Booking source and channel
    booking_source = models.CharField(
        _('Booking Source'),
        max_length=50,
        choices=[
            ('direct', _('Direct')),
            ('phone', _('Phone')),
            ('email', _('Email')),
            ('website', _('Website')),
            ('walk_in', _('Walk-in')),
            ('agent', _('Travel Agent')),
            ('online', _('Online Platform')),
        ],
        default='direct'
    )
    
    # Check-in/out information
    actual_check_in = models.DateTimeField(_('Actual Check-in Time'), null=True, blank=True)
    actual_check_out = models.DateTimeField(_('Actual Check-out Time'), null=True, blank=True)
    early_check_in = models.BooleanField(_('Early Check-in'), default=False)
    late_check_out = models.BooleanField(_('Late Check-out'), default=False)
    
    # Soft delete and audit fields
    is_trash = models.BooleanField(_('Moved to Trash'), default=False, db_index=True)
    created_at = models.DateTimeField(_('Created At'), default=timezone.now)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    cancelled_at = models.DateTimeField(_('Cancelled At'), null=True, blank=True)
    cancellation_reason = models.TextField(_('Cancellation Reason'), blank=True)

    class Meta:
        verbose_name = _('Booking')
        verbose_name_plural = _('Bookings')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['booking_reference']),  # Added this index
            models.Index(fields=['check_in', 'check_out']),
            models.Index(fields=['status', 'is_trash']),
            models.Index(fields=['room', 'status']),
            models.Index(fields=['primary_guest']),
            models.Index(fields=['created_at']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['room', 'check_in', 'check_out'],
                name='unique_booking_per_room_dates_v2',
                condition=models.Q(
                    status__in=['reserved', 'confirmed', 'checked_in'],
                    is_trash=False
                )
            ),
            models.CheckConstraint(
                check=models.Q(check_in__lt=models.F('check_out')),
                name='check_in_before_check_out_v2'
            ),
            models.CheckConstraint(
                check=models.Q(adults__gte=1),
                name='minimum_one_adult'
            )
        ]

    def __str__(self):
        return f"Booking #{self.booking_reference or self.id} - {self.primary_guest.full_name} ({self.room})"

    def save(self, *args, **kwargs):
        # Generate booking reference if not exists
        if not self.booking_reference:
            self.booking_reference = self.generate_unique_booking_reference()
        
        # Set room rate from room's current price if not set
        if not self.room_rate and hasattr(self, 'room') and self.room:
            self.room_rate = self.room.get_final_price()
        
        # Calculate total amount
        self.calculate_total_amount()
        
        super().save(*args, **kwargs)

    def generate_unique_booking_reference(self):
        """Generate unique booking reference with collision handling"""
        import uuid
        from datetime import datetime
        
        # Use the booking's creation date if available, otherwise current date
        if hasattr(self, 'created_at') and self.created_at:
            date_str = self.created_at.strftime('%Y%m%d')
        else:
            date_str = datetime.now().strftime('%Y%m%d')
        
        # Try to generate a unique reference
        max_attempts = 50
        for attempt in range(max_attempts):
            if attempt == 0:
                # First attempt: use standard format
                random_str = str(uuid.uuid4())[:4].upper()
                reference = f"BK-{date_str}-{random_str}"
            else:
                # Subsequent attempts: add more randomness
                random_str = str(uuid.uuid4())[:6].upper()
                reference = f"BK-{date_str}-{random_str}"
            
            # Check if this reference already exists
            if not Booking.objects.filter(booking_reference=reference).exists():
                return reference
        
        # Fallback: use timestamp with microseconds for uniqueness
        timestamp = datetime.now().strftime('%H%M%S%f')[:10]
        return f"BK-{date_str}-{timestamp}"

    def calculate_total_amount(self):
        """Calculate total booking amount"""
        if self.room_rate:
            subtotal = self.room_rate * self.nights
            total = subtotal - self.discount_amount + self.tax_amount
            self.total_amount = max(total, Decimal('0.00'))

    @property
    def nights(self):
        """Calculate number of nights"""
        return (self.check_out - self.check_in).days

    @property
    def total_guests(self):
        """Get total number of guests"""
        return self.adults + self.children

    @property
    def is_active(self):
        """Check if booking is active (not cancelled or checked out)"""
        return self.status in ['reserved', 'confirmed', 'checked_in'] and not self.is_trash

    @property
    def is_current(self):
        """Check if booking is currently active (guest is in hotel)"""
        today = timezone.now().date()
        return (
            self.check_in <= today < self.check_out and 
            self.status == 'checked_in' and 
            not self.is_trash
        )

    @property
    def days_until_checkin(self):
        """Get days until check-in"""
        today = timezone.now().date()
        if self.check_in > today:
            return (self.check_in - today).days
        return 0

    @property
    def balance_due(self):
        """Calculate remaining balance"""
        return self.total_amount - self.advance_payment

    def clean(self):
        """Custom validation"""
        super().clean()
        
        # Validate dates
        if self.check_in and self.check_out:
            if self.check_in >= self.check_out:
                raise ValidationError(_('Check-out date must be after check-in date'))
            
            if self.check_in < timezone.now().date() and not self.pk:
                raise ValidationError(_('Check-in date cannot be in the past'))
        
        # Validate guest capacity
        if hasattr(self, 'room') and self.total_guests > self.room.capacity:
            raise ValidationError(
                _('Total guests ({}) cannot exceed room capacity ({})').format(
                    self.total_guests, self.room.capacity
                )
            )

    def can_cancel(self):
        """Check if booking can be cancelled"""
        return self.status in ['reserved', 'confirmed'] and not self.is_trash

    def can_check_in(self):
        """Check if guest can check in"""
        today = timezone.now().date()
        return (
            self.status in ['reserved', 'confirmed'] and
            self.check_in <= today and
            not self.is_trash
        )

    def can_check_out(self):
        """Check if guest can check out"""
        return self.status == 'checked_in' and not self.is_trash