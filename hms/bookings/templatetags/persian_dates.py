from django import template
import jdatetime
from django.utils import timezone

register = template.Library()

@register.filter
def to_persian_date(value):
    if not value:
        return ''
    gregorian_date = value
    if timezone.is_aware(gregorian_date):
        gregorian_date = timezone.localtime(gregorian_date)
    jalali_date = jdatetime.date.fromgregorian(
        day=gregorian_date.day,
        month=gregorian_date.month,
        year=gregorian_date.year
    )
    return jalali_date.strftime('%Y/%m/%d')

@register.filter
def to_persian_datetime(value):
    if not value:
        return ''
    gregorian_datetime = value
    if timezone.is_aware(gregorian_datetime):
        gregorian_datetime = timezone.localtime(gregorian_datetime)
    jalali_datetime = jdatetime.datetime.fromgregorian(datetime=gregorian_datetime)
    return jalali_datetime.strftime('%Y/%m/%d %H:%M')