from django.db import models

class HotelSettings(models.Model):
    site_name = models.CharField(max_length=100, default="Hotel Management System")
    logo = models.ImageField(upload_to='settings/', blank=True, null=True)
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    email = models.EmailField(blank=True)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=9.0)
    currency = models.CharField(max_length=10, default='IRR')

    def save(self, *args, **kwargs):
        self.pk = 1  # Always use the same pk for singleton
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj