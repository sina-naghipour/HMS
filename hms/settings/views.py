from django.shortcuts import render
from django.views import View



class General(View):
    template_name = 'settings/general.html'
    def get(self, request):
        return render(request, self.template_name)


class Payment(View):
    template_name = 'settings/payment.html'
    def get(self, request):
        return render(request, self.template_name)



class Email(View):
    template_name = 'settings/email.html'
    def get(self, request):
        return render(request, self.template_name)

