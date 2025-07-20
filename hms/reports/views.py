from django.shortcuts import render
from django.views import View


class Occupancy(View):
    template_name = 'reports/occupancy.html'
    def get(self, request):
        return render(request, self.template_name)


class Revenue(View):
    template_name = 'reports/revenue.html'
    def get(self, request):
        return render(request, self.template_name)


class Custom(View):
    template_name = 'reports/custom.html'
    def get(self, request):
        return render(request, self.template_name)

