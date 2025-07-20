from django.shortcuts import render
from django.views import View


class ListGuests(View):
    template_name = 'guests/list.html'
    def get(self, request):
        return render(request, self.template_name)


class DetailGuests(View):
    template_name = 'guests/detail.html'
    def get(self, request):
        return render(request, self.template_name)



class CreateGuests(View):
    template_name = 'guests/create.html'
    def get(self, request):
        return render(request, self.template_name)



