from django.shortcuts import render
from django.views import View


class ListStaff(View):
    template_name = 'staff/list.html'
    def get(self, request):
        return render(request, self.template_name)


class DetailStaff(View):
    template_name = 'staff/detail.html'
    def get(self, request):
        return render(request, self.template_name)

