from django import forms
from .models import Room, Amenity, RoomType

class RoomForm(forms.ModelForm):
    amenities = forms.ModelMultipleChoiceField(
        queryset=Amenity.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Room
        fields = [
            'number', 
            'room_type', 
            'floor', 
            'capacity', 
            'price', 
            'status', 
            'amenities', 
            'description'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['room_type'].queryset = RoomType.objects.all()
        self.fields['status'].initial = 'available'