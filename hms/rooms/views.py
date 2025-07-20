from django.shortcuts import render
from django.views import View


class Home(View):
    template_name = 'dashboard.html'
    def get(self, request):
        return render(request, self.template_name)


class ListRooms(View):
    template_name = 'rooms/list.html'
    def get(self, request):
        return render(request, self.template_name)


class DetailRooms(View):
    template_name = 'rooms/detail.html'
    def get(self, request):
        return render(request, self.template_name)



class CreateRooms(View):
    template_name = 'rooms/create.html'
    def get(self, request):
        return render(request, self.template_name)




class DetailTypes(View):
    template_name = 'rooms/types/detail.html'
    def get(self, request):
        return render(request, self.template_name)


class ListTypes(View):
    template_name = 'rooms/types/list.html'
    def get(self, request):
        return render(request, self.template_name)

