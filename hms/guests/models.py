from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

class Guest(models.Model):
    GENDER_CHOICES = [
        ('M', _('Male')),
        ('F', _('Female')),
        ('O', _('Other'))
    ]
    
    national_id = models.CharField(
        _('National ID'),
        max_length=20,  # Increased for international IDs
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z0-9]{5,20}$',
                message=_('National ID must be 5-20 alphanumeric characters')
            )
        ],
        db_index=True
    )
    first_name = models.CharField(_('First Name'), max_length=100)
    last_name = models.CharField(_('Last Name'), max_length=100)
    gender = models.CharField(
        _('Gender'),
        max_length=1,
        choices=GENDER_CHOICES,
        default='O'
    )
    phone = models.CharField(
        _('Phone Number'),
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message=_('Phone number must be entered in format: "+999999999". Up to 15 digits allowed.')
            )
        ]
    )
    email = models.EmailField(_('Email'), blank=True)
    address = models.TextField(_('Address'), blank=True)
    date_of_birth = models.DateField(_('Date of Birth'), null=True, blank=True)
    nationality = models.CharField(_('Nationality'), max_length=100, blank=True)
    passport_number = models.CharField(_('Passport Number'), max_length=20, blank=True)
    
    booking = models.ForeignKey(
        'bookings.Booking',
        verbose_name=_('Booking'),
        on_delete=models.CASCADE,
        related_name='guests',
        null=True,
        blank=True
    )
    is_primary = models.BooleanField(_('Primary Guest'), default=False)
    
    # Audit fields
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    created_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_guests'
    )

    class Meta:
        verbose_name = _('Guest')
        verbose_name_plural = _('Guests')
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['national_id']),
            models.Index(fields=['booking', 'is_primary']),
            models.Index(fields=['phone']),
            models.Index(fields=['email']),
        ]
        constraints = [
            # Ensure only one primary guest per booking
            models.UniqueConstraint(
                fields=['booking'],
                name='unique_primary_guest_per_booking',
                condition=models.Q(is_primary=True)
            ),
            # Prevent duplicate guests in same booking
            models.UniqueConstraint(
                fields=['national_id', 'booking'],
                name='unique_guest_per_booking'
            )
        ]

    def __str__(self):
        return f"{self.full_name} ({self.national_id})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def age(self):
        """Calculate age from date of birth"""
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None

    def clean(self):
        """Custom validation"""
        super().clean()
        
        # Validate that primary guest must have a booking
        if self.is_primary and not self.booking:
            raise ValidationError(_('Primary guest must be associated with a booking'))
        
        # Validate age if date_of_birth is provided
        if self.date_of_birth:
            from datetime import date
            if self.date_of_birth > date.today():
                raise ValidationError(_('Date of birth cannot be in the future'))

    def save(self, *args, **kwargs):
        self.full_clean()
        
        # Ensure only one primary guest per booking
        if self.is_primary and self.booking:
            Guest.objects.filter(
                booking=self.booking, 
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        
        super().save(*args, **kwargs)