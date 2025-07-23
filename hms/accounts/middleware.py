from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        response = self.get_response(request)
        return response
        
    def process_view(self, request, view_func, view_args, view_kwargs):
        # dont need login.
        exempt_urls = [
            reverse('accounts:login'),
            reverse('accounts:register'),
        ]
        # need login
        protected_urls = [
            reverse('accounts:dashboard'),
            reverse('accounts:logout'),
            reverse('bookings:list'),
            reverse('bookings:detail', kwargs={'pk' : 0}),
            reverse('bookings:create'),
            reverse('bookings:create'),
            reverse('bookings:calendar'),
            reverse('guests:list'),
            reverse('guests:detail', kwargs={'pk' : 0}),
            reverse('reports:occupancy'),
            reverse('reports:revenue'),
            reverse('reports:custom'),
            reverse('rooms:list'),
            reverse('rooms:detail', kwargs={'number': 101}),
            reverse('rooms:create'),
            reverse('rooms:types_list'),
            reverse('rooms:types_detail', kwargs={'pk' : 0}),
            reverse('services:list'),
            reverse('services:detail'),
            reverse('settings:general'),
            reverse('settings:payment'),
            reverse('settings:email'),
            reverse('staff:list'),
            reverse('staff:detail', kwargs={'pk' : 0}),
            reverse('staff:edit', kwargs={'pk' : 0}),
            reverse('staff:delete', kwargs={'pk' : 0}),
            reverse('staff:create'),
            
        ]
        
        path = request.path
        is_protected = any(path.startswith(url) for url in protected_urls)
        is_exempt = any(path.startswith(url) for url in exempt_urls)
        
        if is_protected and not is_exempt:
            if not request.user.is_authenticated:
                login_url = reverse(settings.LOGIN_URL) if hasattr(settings, 'LOGIN_URL') else reverse('accounts:login')
                return HttpResponseRedirect(f"{login_url}?next={path}")
        
        return None