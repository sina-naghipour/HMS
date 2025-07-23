from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Booking
from rooms.models import Room
from guests.models import Guest
from django.db.models import Prefetch
import jdatetime
from django.views import View
from django.http import JsonResponse
from datetime import datetime
import hashlib
from django.db import IntegrityError
from django.db import transaction


class BookingListView(ListView):
    model = Booking
    template_name = 'bookings/list.html'
    context_object_name = 'bookings'
    paginate_by = 20

    def get_queryset(self):
        # Start with non-trashed items
        queryset = super().get_queryset().filter(is_trash=False)
        
        # Optional: Add trash view
        if self.request.GET.get('show_trash'):
            queryset = super().get_queryset().filter(is_trash=True)
        
        # Status filter
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.select_related('room', 'primary_guest')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = dict(Booking.STATUS_CHOICES)
        context['current_status'] = self.request.GET.get('status')
        context['showing_trash'] = bool(self.request.GET.get('show_trash'))
        return context

class BookingDetailView(DetailView):
    model = Booking
    template_name = 'bookings/detail.html'
    context_object_name = 'booking'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"جزئیات رزرو #{self.object.id}"
        return context


class BookingCreateView(CreateView):
    model = Booking
    template_name = 'bookings/create.html'
    fields = ['room', 'check_in', 'check_out', 'special_requests']
    success_url = reverse_lazy('bookings:list')

    @transaction.atomic
    def form_valid(self, form):
        try:
            room = form.cleaned_data['room']
            check_in = form.cleaned_data['check_in']
            check_out = form.cleaned_data['check_out']
            
            conflicting = Booking.objects.select_for_update().filter(
                room=room,
                check_out__gt=check_in,
                check_in__lt=check_out,
                status__in=['reserved', 'checked_in']
            ).exists()
            
            if conflicting:
                messages.error(self.request, 'این اتاق در تاریخ انتخابی قبلاً رزرو شده است')
                return self.form_invalid(form)
            
            # Validate dates
            if check_in < timezone.now().date():
                messages.error(self.request, 'تاریخ ورود نمی‌تواند در گذشته باشد')
                return self.form_invalid(form)
                
            if check_out <= check_in:
                messages.error(self.request, 'تاریخ خروج باید بعد از تاریخ ورود باشد')
                return self.form_invalid(form)

            primary_guest = Guest.objects.create(
                national_id=self.request.POST.get('guest_national_id'),
                first_name=self.request.POST.get('guest_first_name'),
                last_name=self.request.POST.get('guest_last_name'),
                gender=self.request.POST.get('guest_gender', 'O'),
                phone=self.request.POST.get('guest_phone'),
                email=self.request.POST.get('guest_email', ''),
                address=self.request.POST.get('guest_address', ''),
                is_primary=True,
            )
            
            form.instance.status = 'reserved'
            form.instance.assigned_staff = self.request.user
            form.instance.primary_guest = primary_guest
            
            booking = form.save()
            primary_guest.booking = booking
            primary_guest.save()

            additional_national_ids = self.request.POST.getlist('additional_guests_national_id[]')
            additional_first_names = self.request.POST.getlist('additional_guests_first_name[]')
            additional_last_names = self.request.POST.getlist('additional_guests_last_name[]')
            additional_phones = self.request.POST.getlist('additional_guests_phone[]')
            additional_genders = self.request.POST.getlist('additional_guests_gender[]')
            
            for i in range(len(additional_national_ids)):
                Guest.objects.create(
                    national_id=additional_national_ids[i],
                    first_name=additional_first_names[i],
                    last_name=additional_last_names[i],
                    gender=additional_genders[i] if i < len(additional_genders) else 'O',
                    phone=additional_phones[i] if i < len(additional_phones) else '',
                    booking=booking,
                    is_primary=False,
                )

            messages.success(self.request, 'رزرو با موفقیت ایجاد شد')
            return redirect(self.success_url)

        except IntegrityError:
            messages.error(self.request, 'خطایی در ایجاد رزرو رخ داد. لطفاً دوباره تلاش کنید')
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f'خطای سیستمی: {str(e)}')
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "رزرو جدید"
        context['available_rooms'] = Room.objects.filter(status='available')
        context['gender_choices'] = Guest.GENDER_CHOICES
        
        # Get all booked dates for each room
        booked_dates = {}
        for room in context['available_rooms']:
            bookings = Booking.objects.filter(
                room=room,
                status__in=['reserved', 'checked_in']
            ).values_list('check_in', 'check_out')
            booked_dates[room.id] = list(bookings)
        
        context['booked_dates'] = booked_dates
        return context



class BookingUpdateView(UpdateView):
    model = Booking
    template_name = 'bookings/edit.html'
    fields = ['room', 'check_in', 'check_out', 'status', 'special_requests']
    success_url = reverse_lazy('bookings:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"ویرایش رزرو #{self.object.id}"
        context['booking'] = self.object
        
        # Get currently available rooms
        context['available_rooms'] = Room.objects.filter(status='available')
        
        # Get all rooms for fallback (if current room isn't available)
        context['all_rooms'] = Room.objects.all()
        
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'رزرو با موفقیت بروزرسانی شد')
        return response


class BookingCalendarView(TemplateView):
    template_name = 'bookings/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get current Persian month and year
        today = jdatetime.date.today()
        context['current_month'] = today.strftime('%B %Y')
        
        return context




class BookingCalendarEventsView(View):
    def get(self, request):
        try:
            bookings = Booking.objects.select_related('room', 'primary_guest')
            
            # Create a color map for rooms
            room_colors = self.generate_room_colors()
            
            events = []
            for booking in bookings:
                room_color = room_colors.get(booking.room_id, '#3B82F6')  # Default blue if not found
                
                events.append({
                    'id': booking.id,
                    'title': f'اتاق {booking.room.number} - {booking.primary_guest.full_name}',
                    'start': booking.check_in.isoformat(),
                    'end': booking.check_out.isoformat(),
                    'color': room_color,
                    'textColor': self.get_text_color(room_color),
                    'extendedProps': {
                        'status': booking.status,
                        'room_number': booking.room.number,
                        'guest_name': booking.primary_guest.full_name,
                        'room_id': booking.room_id
                    }
                })
            
            return JsonResponse(events, safe=False)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def generate_room_colors(self):
        """Generate a consistent color map for all rooms"""
        rooms = Room.objects.all()
        color_map = {}
        
        # A palette of distinct colors
        color_palette = [
            '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
            '#EC4899', '#14B8A6', '#F97316', '#84CC16', '#06B6D4',
            '#6366F1', '#A855F7', '#D946EF', '#F43F5E', '#0EA5E9',
            '#64748B', '#78716C', '#B91C1C', '#C2410C', '#4C1D95'
        ]
        
        # Assign colors to rooms
        for i, room in enumerate(rooms):
            color_index = i % len(color_palette)
            color_map[room.id] = color_palette[color_index]
            
        return color_map
    
    def get_text_color(self, bg_color):
        """Determine if text should be black or white based on background brightness"""
        # Convert hex to RGB
        r = int(bg_color[1:3], 16)
        g = int(bg_color[3:5], 16)
        b = int(bg_color[5:7], 16)
        
        # Calculate brightness
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        
        return '#000000' if brightness > 128 else '#ffffff'
    
    
class BookingDeleteView(DeleteView):
    model = Booking
    success_url = reverse_lazy('bookings:list')
    template_name = 'bookings/booking_confirm_delete.html'

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: Mark the booking as trash instead of deleting.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        
        # Perform soft delete
        self.object.is_trash = True
        self.object.save()
        
        messages.success(request, 'رزرو با موفقیت به سطل زباله منتقل شد')
        return redirect(success_url)

    # Disable the normal delete behavior
    def delete(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "حذف رزرو"
        context['message'] = "آیا از انتقال این رزرو به سطل زباله اطمینان دارید؟"
        return context