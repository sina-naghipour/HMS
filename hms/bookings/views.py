from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Booking
from rooms.models import Room
from guests.models import Guest

class BookingListView(ListView):
    model = Booking
    template_name = 'bookings/list.html'
    context_object_name = 'bookings'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset.select_related('guest', 'room')

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

    def form_valid(self, form):
        form.instance.status = 'reserved'
        
        # Create primary guest
        primary_guest = Guest.objects.create(
            national_id=self.request.POST.get('guest_national_id'),
            first_name=self.request.POST.get('guest_first_name'),
            last_name=self.request.POST.get('guest_last_name'),
            gender=self.request.POST.get('guest_gender', 'O'),
            phone=self.request.POST.get('guest_phone'),
            email=self.request.POST.get('guest_email', ''),
            address=self.request.POST.get('guest_address', '')
        )
        form.instance.guest = primary_guest
        
        # Save the booking first
        booking = form.save()
        
        # Handle additional guests
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
                reservation=booking
            )
        
        messages.success(self.request, 'رزرو با موفقیت ایجاد شد')
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "رزرو جدید"
        context['available_rooms'] = Room.objects.filter(status='available')
        context['gender_choices'] = Guest.GENDER_CHOICES
        return context
    
class BookingUpdateView(UpdateView):
    model = Booking
    template_name = 'bookings/create.html'
    fields = ['guest', 'room', 'check_in', 'check_out', 'adults', 'children', 'status', 'special_requests']
    success_url = reverse_lazy('bookings:list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'رزرو با موفقیت بروزرسانی شد')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"ویرایش رزرو #{self.object.id}"
        return context

class BookingCalendarView(ListView):
    model = Booking
    template_name = 'bookings/calendar.html'
    
    def get_queryset(self):
        month = self.request.GET.get('month')
        year = self.request.GET.get('year')
        
        if month and year:
            date = timezone.datetime(int(year), int(month), 1)
        else:
            date = timezone.now()
        
        start_date = date.replace(day=1)
        if start_date.month == 12:
            end_date = start_date.replace(year=start_date.year+1, month=1)
        else:
            end_date = start_date.replace(month=start_date.month+1)
        
        return Booking.objects.filter(
            check_out__gte=start_date,
            check_in__lte=end_date
        ).select_related('guest', 'room')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calendar logic
        month = self.request.GET.get('month')
        year = self.request.GET.get('year')
        
        if month and year:
            date = timezone.datetime(int(year), int(month), 1)
        else:
            date = timezone.now()
        
        context['calendar_date'] = date
        context['title'] = f"تقویم رزروها - {date.strftime('%B %Y')}"
        return context