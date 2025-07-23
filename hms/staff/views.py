from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import StaffCreationForm, StaffChangeForm
from django.db import models
from bookings.models import Booking
from django.utils import timezone
from django.shortcuts import redirect
User = get_user_model()


class ListStaffView(ListView):
    model = User
    template_name = 'staff/list.html'  # Make sure this matches your template path
    context_object_name = 'staff_members'
    paginate_by = 15  # Number of items per page

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_staff=True)
        
        # Search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                models.Q(first_name__icontains=search_query) |
                models.Q(last_name__icontains=search_query) |
                models.Q(email__icontains=search_query)
            )
        # Filter by status if needed
        status_filter = self.request.GET.get('status')
        if status_filter == 'active':
            queryset = queryset.filter(is_active=True)
        elif status_filter == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        return queryset.order_by('-date_joined')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add search query to context
        context['search_query'] = self.request.GET.get('q', '')
        
        # Add status filter to context
        context['status_filter'] = self.request.GET.get('status', 'all')
        
        return context


class DetailStaffView(DetailView):
    model = User
    template_name = 'staff/detail.html'
    context_object_name = 'staff'  # This ensures the object is available as 'staff' in template
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        staff = self.object  # Get the staff member being viewed
        
        # Get all bookings for this staff member
        bookings = Booking.objects.filter(assigned_staff=staff)
        
        context.update({
            'total_bookings': bookings.count(),
            'active_bookings': bookings.filter(status='checked_in').count(),
            'completed_bookings': bookings.filter(status='checked_out').count(),
            'cancelled_bookings': bookings.filter(status='cancelled').count(),
            'total_revenue': sum(b.total_price for b in bookings if b.total_price),
        })
        return context
    


    def get_recent_activity(self, staff):
        """Get recent activity related to this staff member"""
        # Example: Get last 5 bookings handled by this staff
        return Booking.objects.filter(assigned_staff=staff).order_by('-created_at')[:5]
    
    def get_staff_stats(self, staff):
        """Get statistics about this staff member's performance"""
        bookings = Booking.objects.filter(assigned_staff=staff)
        
        return {
            'total_bookings': bookings.count(),
            'active_bookings': bookings.filter(status='checked_in').count(),
            'completed_bookings': bookings.filter(status='checked_out').count(),
            'cancelled_bookings': bookings.filter(status='cancelled').count(),
            'revenue_generated': sum(b.total_price for b in bookings if b.total_price),
        }


class CreateStaffView(CreateView):
    model = User
    form_class = StaffCreationForm
    template_name = 'staff/create.html'
    success_url = reverse_lazy('staff:list')

    def form_valid(self, form):
        form.instance.is_staff = True
        response = super().form_valid(form)
        messages.success(self.request, 'کارمند جدید با موفقیت ایجاد شد')
        return response



class UpdateStaffView(UpdateView):
    model = User
    form_class = StaffChangeForm
    template_name = 'staff/edit.html'
    success_url = reverse_lazy('staff:list')

    def get_success_url(self):
        messages.success(self.request, 'اطلاعات کارمند با موفقیت بروزرسانی شد')
        return super().get_success_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"ویرایش {self.object.get_full_name()}"
        context['staff'] = self.object
        return context



class DeleteStaffView(DeleteView):
    model = User
    success_url = reverse_lazy('staff:list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        fallback_user = User.objects.get(username='root')
        
        Booking.objects.filter(assigned_staff=self.object).update(assigned_staff=fallback_user)
        
        self.object.delete()
        
        messages.success(request, f'کارمند {self.object.get_full_name()} با موفقیت حذف شد و رزروها به کاربر دیگری منتقل شد')
        return redirect(self.success_url())