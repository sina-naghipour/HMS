from django.shortcuts import render, redirect
from django.views import View
from accounts.forms import LoginForm, RegisterForm
from django.contrib.auth import login, authenticate, logout
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
from .forms import LoginForm, RegisterForm

from django.contrib.auth import logout
from django.contrib import messages
from django.utils.translation import gettext as _
from django.views import View
from django.shortcuts import redirect





class Dashboard(View):
    template_name = 'admin/dashboard.html'
    def get(self, request):
        return render(request, self.template_name)


class LoginView(View):
    template_name = 'registeration/login.html'
    redirect_authenticated_user = True
    success_url = 'accounts:dashboard'

    @method_decorator(sensitive_post_parameters('password'))
    @method_decorator(never_cache)
    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request, 'session') or not request.session.session_key:
            request.session.save()
        
        try:
            if self.redirect_authenticated_user and request.user.is_authenticated:
                messages.info(request, _("You're already logged in!"))
                return redirect(self.success_url)
        except Exception as e:
            request.session.flush()
            request.session.save()
        
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = LoginForm()
        
        if not request.session.session_key:
            request.session.create()
            
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if not request.session.session_key:
            request.session.create()
            
        form = LoginForm(request, data=request.POST)
        
        if not form.is_valid():
            return self.render_form_errors(request, form)

        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')

        try:
            user = authenticate(request, username=username, password=password)
            
            if user is None:
                messages.error(request, _("Invalid username or password."))
                return self.render_form_errors(request, form)
            
            if not user.is_active:
                messages.error(request, _("This account is inactive."))
                return self.render_form_errors(request, form)

            request.session.cycle_key()
            login(request, user)
            
            messages.success(request, _("Successfully logged in!"))
            next_url = request.GET.get('next', self.success_url)
            return redirect(next_url)
            
        except Exception as e:
            request.session.flush()
            messages.error(request, _("An error occurred. Please try again."))
            return render(request, self.template_name, {'form': form})
class RegisterView(View):
    template_name = 'registeration/register.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            messages.info(request, _("You're already registered and logged in!"))
            return redirect('accounts:dashboard')
            
        form = RegisterForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = RegisterForm(request.POST)
        
        if form.is_valid():
            try:
                user = form.save(commit=False)
                
                if not self.validate_user(user):
                    return render(request, self.template_name, {'form': form})
                
                user.save()
                login(request, user)
                
                messages.success(request, _("Registration successful! You're now logged in."))
                return redirect('accounts:dashboard')
                
            except ValidationError as e:
                messages.error(request, e.message)
            except Exception as e:
                messages.error(request, _("An error occurred during registration. Please try again."))
        
        if not form.errors:
            messages.error(request, _("Please correct the errors below."))
        return render(request, self.template_name, {'form': form})
    
    def validate_user(self, user):
        """Additional validation logic if needed"""
        if 'example.com' in user.email:
            messages.error(self.request, _("Registration with this email domain is not allowed."))
            return False
        return True


class LogoutView(View):
    @method_decorator(csrf_protect)
    @method_decorator(require_POST)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        if request.user.is_authenticated:
            logout(request)
            request.session.flush()
            messages.success(request, _("You've been successfully logged out."))
            
            # Create a redirect response with cache-control headers
            response = redirect('accounts:login')
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '-1'
            return response
        
        messages.info(request, _("You weren't logged in."))
        return redirect('accounts:login')