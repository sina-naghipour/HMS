from django.shortcuts import render
from django.views import View


class ListServices(View):
    template_name = 'services/list.html'
    def get(self, request):
        return render(request, self.template_name)


class DetailServices(View):
    template_name = 'services/detail.html'
    def get(self, request):
        return render(request, self.template_name)


