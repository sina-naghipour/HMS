from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

User = get_user_model()

# forms.py
class StaffCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
        labels = {
            'username': 'نام کاربری',
            'email': 'ایمیل',
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'is_staff': 'کارمند است',
            'is_active': 'فعال است',
        }
        help_texts = {
            'username': 'نام کاربری باید منحصر به فرد باشد',
            'email': 'ایمیل معتبر وارد کنید',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Tailwind classes to all fields
        for field_name, field in self.fields.items():
            if field_name not in ['is_staff', 'is_active']:
                field.widget.attrs.update({
                    'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600'
                })
            else:
                # Special styling for checkboxes
                field.widget.attrs.update({
                    'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600'
                })

class StaffChangeForm(UserChangeForm):
    password = forms.CharField(
        label="رمز عبور جدید",
        widget=forms.PasswordInput,
        required=False,
        help_text="برای تغییر رمز عبور، رمز جدید را وارد کنید. در صورت عدم تمایل خالی بگذارید."
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'password')
        labels = {
            'username': 'نام کاربری',
            'email': 'ایمیل',
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'is_staff': 'کارمند است',
            'is_active': 'فعال است',
        }
        help_texts = {
            'username': 'نام کاربری باید منحصر به فرد باشد',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Remove the default password help text
        self.fields['password'].help_text = None
        
        # Apply consistent styling
        base_style = 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600'
        checkbox_style = 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600'
        
        for field_name, field in self.fields.items():
            if field_name in ['is_staff', 'is_active']:
                field.widget.attrs.update({'class': checkbox_style})
            else:
                field.widget.attrs.update({'class': base_style})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user

