from django.db import models
from django.utils.translation import gettext_lazy as _
from rooms.models import Room
from guests.models import Guest

class Booking(models.Model):
    STATUS_CHOICES = [
        ('reserved', _('Reserved')),
        ('checked_in', _('Checked In')),
        ('checked_out', _('Checked Out')),
        ('cancelled', _('Cancelled')),
    ]

    room = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        verbose_name=_('Room'),
        related_name='bookings'
    )
    check_in = models.DateField(_('Check In Date'))
    check_out = models.DateField(_('Check Out Date'))
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='reserved'
    )
    primary_guest = models.ForeignKey(
        'guests.Guest',
        on_delete=models.PROTECT,
        related_name='primary_bookings',
        null=False
    )
    assigned_staff = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.PROTECT,
        related_name='staff_bookings',
        null=False,
    )
    is_trash = models.BooleanField(default=False)
    special_requests = models.TextField(_('Special Requests'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Booking')
        verbose_name_plural = _('Bookings')
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['room', 'check_in', 'check_out'],
                name='unique_booking_per_room_dates',
                condition=models.Q(status__in=['reserved', 'checked_in'])
            ),
            models.CheckConstraint(
                check=models.Q(check_in__lt=models.F('check_out')),
                name='check_in_before_check_out'
            )
        ]

    def __str__(self):
        return f"Booking #{self.id} - {self.guests} ({self.room})"

    @property
    def nights(self):
        return (self.check_out - self.check_in).days

    @property
    def total_price(self):
        return self.room.price * self.nights