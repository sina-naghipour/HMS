from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView
from django.urls import reverse_lazy
from rooms.forms import RoomForm
from rooms.models import RoomType, Amenity, Room
from django.db import models
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import RoomType, Amenity
import re


class Home(View):
    template_name = 'dashboard.html'
    def get(self, request):
        return render(request, self.template_name)


class ListRooms(ListView):
    model = Room
    template_name = 'rooms/list.html'
    context_object_name = 'rooms'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['room_types'] = RoomType.objects.all()
        return context


class CreateRooms(CreateView):
    model = Room
    form_class = RoomForm
    template_name = 'rooms/create.html'
    success_url = reverse_lazy('rooms:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['room_types'] = RoomType.objects.all()
        context['amenities'] = Amenity.objects.all()
        context['title'] = "افزودن اتاق جدید"
        return context





class DetailRooms(View):
    template_name = 'rooms/detail.html'
    
    def get(self, request, number):
        room = get_object_or_404(Room, number=number)
        return render(request, self.template_name, {'room': room})


class EditRoomView(View):
    template_name = 'rooms/edit.html'  # Path to your edit template
    
    def get(self, request, number):
        room = get_object_or_404(Room, number=number)
        form = RoomForm(instance=room)
        
        context = {
            'room': room,
            'room_types': RoomType.objects.all(),
            'status_choices': Room.StatusChoices.choices,
            'amenities': Amenity.objects.all(),
            'form': form,  # Using the form we'll create
        }
        return render(request, self.template_name, context)
    
    def post(self, request, number):
        room = get_object_or_404(Room, number=number)
        form = RoomForm(request.POST, instance=room)
        
        if form.is_valid():
            form.save()
            return redirect('rooms:detail', number=number)
        
        # If form is invalid, re-render the page with errors
        context = {
            'room': room,
            'room_types': RoomType.objects.all(),
            'status_choices': Room.StatusChoices.choices,
            'amenities': Amenity.objects.all(),
            'form': form,
        }
        return render(request, self.template_name, context)
    

class DeleteRoomView(View):
    def post(self, request, number):
        room = get_object_or_404(Room, number=number)
        room_number = room.number
        room.delete()
        return redirect('rooms:list')
    


class RoomTypeDetailView(View):
    template_name = 'rooms/types/detail.html'
    
    def calculate_occupancy_rate(self, room_type):
        """Calculate occupancy rate percentage for the room type"""

        total_rooms = room_type.rooms.count()
        if total_rooms == 0:
            return 0
        occupied_rooms = room_type.rooms.filter(status='occupied').count()
        return round((occupied_rooms / total_rooms) * 100, 2)
    
    def calculate_avg_revenue(self, room_type):
        """Calculate average revenue for the room type"""

        avg_price = room_type.rooms.aggregate(avg=models.Avg('price'))['avg'] or 0
        return round(avg_price * (self.calculate_occupancy_rate(room_type) / 100), 2)
    
    def get_popular_amenities(self, room_type):
        """Get popular amenities with their usage percentages"""
        amenities = Amenity.objects.filter(room__room_type=room_type).annotate(
            usage_count=models.Count('room')
        ).order_by('-usage_count')[:3]
        
        total_rooms = room_type.rooms.count()
        if total_rooms == 0:
            return []
            
        return [
            {
                'name': amenity.name,
                'percentage': round((amenity.usage_count / total_rooms) * 100, 2)
            }
            for amenity in amenities
        ]
    
    def get(self, request, pk):
        room_type = get_object_or_404(
            RoomType.objects.annotate(
                price_min=models.Min('rooms__price'),
                price_max=models.Max('rooms__price'),
                price_avg=models.Avg('rooms__price'),
                total_rooms=models.Count('rooms')  # Changed from room_count to total_rooms
            ),
            pk=pk
        )
        context = {
            'room_type': room_type,
            'occupancy_rate': self.calculate_occupancy_rate(room_type),
            'avg_revenue': self.calculate_avg_revenue(room_type),
            'popular_amenities': self.get_popular_amenities(room_type),
            'recent_rooms': room_type.rooms.all().order_by('-updated_at')[:3],}
        
        return render(request, self.template_name, context)
    



class ListTypes(View):
    template_name = 'rooms/types/list.html'
    def get(self, request):
        return render(request, self.template_name)




class RoomTypeListView(View):
    template_name = 'rooms/types/list.html'
    
    def get(self, request):
        
        room_types = RoomType.objects.annotate(
            total_rooms=models.Count('rooms'),
            lowest_price=models.Min('rooms__price'),
            highest_price=models.Max('rooms__price')
        ).all()
        
        context = {
            'room_types': room_types
        }
        return render(request, self.template_name, context)


class RoomTypeCreateView(CreateView):
    model = RoomType
    fields = ['name', 'description', 'base_price']  # Removed default_amenities
    template_name = 'rooms/types/create.html'
    success_url = reverse_lazy('rooms:types_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['amenities_help_text'] = "Enter amenities separated by commas (e.g., WiFi, Breakfast, Parking)"
        return context
    
    def form_valid(self, form):
        # First save the RoomType instance to get an ID
        self.object = form.save()
        
        # Process amenities from the submitted form data
        amenities_input = self.request.POST.get('amenities_input', '')
        amenity_names = {name.strip() for name in re.split(r'[,،]', amenities_input) if name.strip()}
        
        # Add amenities to the room type
        for name in amenity_names:
            amenity, _ = Amenity.objects.get_or_create(name=name)
            self.object.default_amenities.add(amenity)
        
        return super().form_valid(form)



class RoomTypeDeleteView(View):
    def post(self, request, pk):
        room_type = get_object_or_404(RoomType, pk=pk)
        
        if room_type.rooms.exists():
            return redirect('rooms:types_list')
        
        room_type.delete()
        return redirect('rooms:types_list')


class RoomTypeEditView(UpdateView):
    model = RoomType
    template_name = 'rooms/types/edit.html'
    fields = ['name', 'description', 'base_price']  # Removed default_amenities
    success_url = reverse_lazy('rooms:types_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"ویرایش نوع اتاق {self.object.name}"
        
        # Get existing amenities as comma-separated string
        existing_amenities = self.object.default_amenities.all()
        context['existing_amenities'] = "، ".join(amenity.name for amenity in existing_amenities)
        
        return context
    
    def form_valid(self, form):
        # First save the basic RoomType fields
        self.object = form.save()
        
        # Process amenities input
        amenities_input = self.request.POST.get('amenities_input', '')
        amenity_names = {name.strip() for name in re.split(r'[,،]', amenities_input) if name.strip()}
        
        # Clear existing amenities
        self.object.default_amenities.clear()
        
        # Add new amenities
        for name in amenity_names:
            amenity, _ = Amenity.objects.get_or_create(name=name)
            self.object.default_amenities.add(amenity)
        
        return super().form_valid(form)