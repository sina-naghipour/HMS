from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from bookings.models import Booking

class Guest(models.Model):
    GENDER_CHOICES = [
        ('M', _('Male')),
        ('F', _('Female')),
        ('O', _('Other'))
    ]
    
    national_id = models.CharField(
        _('National ID'),
        max_length=10,
        validators=[
            RegexValidator(
                regex='^[0-9]{10}$',
                message=_('National ID must be 10 digits')
            )
        ]
    )
    first_name = models.CharField(_('First Name'), max_length=100)
    last_name = models.CharField(_('Last Name'), max_length=100)
    gender = models.CharField(
        _('Gender'),
        max_length=1,
        choices=GENDER_CHOICES
    )
    phone = models.CharField(
        _('Phone Number'),
        max_length=11,
        validators=[
            RegexValidator(
                regex='^[0-9]{11}$',
                message=_('Phone number must be 11 digits')
            )
        ]
    )
    email = models.EmailField(_('Email'), blank=True)
    address = models.TextField(_('Address'), blank=True)
    booking = models.ForeignKey(
        Booking,
        verbose_name=_('Booking'),
        on_delete=models.CASCADE,
        related_name='guests',
        null=True,
        blank=True
    )
    is_primary = models.BooleanField(_('Primary Guest'), default=False)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Guest')
        verbose_name_plural = _('Guests')
        ordering = ['last_name', 'first_name']
        constraints = [
            models.UniqueConstraint(
                fields=['first_name', 'last_name', 'booking'],
                name='unique_guest_per_booking',
                condition=models.Q(is_primary=False)
            ),
            models.UniqueConstraint(
                fields=['booking'],
                name='unique_primary_guest',
                condition=models.Q(is_primary=True)
            )
        ]

    def __str__(self):
        return f"{self.full_name} ({self.national_id})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        # Ensure only one primary guest per booking
        if self.is_primary and self.booking:
            Guest.objects.filter(booking=self.booking, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)