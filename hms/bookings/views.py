from django.shortcuts import render
from django.views import View

class ListBookings(View):
    template_name = 'bookings/list.html'
    def get(self, request):
        return render(request, self.template_name)


class DetailBookings(View):
    template_name = 'bookings/detail.html'
    def get(self, request):
        return render(request, self.template_name)



class CreateBookings(View):
    template_name = 'bookings/create.html'
    def get(self, request):
        return render(request, self.template_name)




class CalendarBookings(View):
    template_name = 'bookings/calendar.html'
    def get(self, request):
        return render(request, self.template_name)
