from django.shortcuts import render
from django.views import View
from guests.models import Guest
from django.db import models
from django.views.generic import DetailView
from django.core.paginator import Paginator


class ListGuests(View):
    template_name = 'guests/list.html'
    paginate_by = 10
    
    def get(self, request):
        guests = Guest.objects.annotate(
            stays_count=models.Count('booking', distinct=True)
        ).select_related('booking').order_by('-created_at')
        
        for guest in guests:
            guest.is_current_guest = guest.booking and guest.booking.status == 'checked_in'
        
        paginator = Paginator(guests, self.paginate_by)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'guests': page_obj,
            'page_obj': page_obj,
        }
        return render(request, self.template_name, context)

class DetailGuests(DetailView):
    model = Guest
    template_name = 'guests/detail.html'
    context_object_name = 'guest'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context here
        return context


class CreateGuests(View):
    template_name = 'guests/create.html'
    def get(self, request):
        return render(request, self.template_name)



