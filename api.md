Authentication
POST /api/v1/auth/register/ - User registration
POST /api/v1/auth/login/ - User login
POST /api/v1/auth/logout/ - User logout
GET/PUT /api/v1/auth/profile/ - User profile
Dashboard
GET /api/v1/dashboard/stats/ - Dashboard statistics
Rooms Management
GET /api/v1/rooms/ - List all rooms
POST /api/v1/rooms/ - Create new room
GET /api/v1/rooms/{number}/ - Get room details
PUT /api/v1/rooms/{number}/ - Update room
DELETE /api/v1/rooms/{number}/ - Delete room
GET /api/v1/rooms/available/ - Get available rooms for date range
Room Types
GET /api/v1/room-types/ - List room types
POST /api/v1/room-types/ - Create room type
GET /api/v1/room-types/{id}/ - Get room type details
PUT /api/v1/room-types/{id}/ - Update room type
DELETE /api/v1/room-types/{id}/ - Delete room type
Amenities
GET /api/v1/amenities/ - List amenities
POST /api/v1/amenities/ - Create amenity
GET /api/v1/amenities/{id}/ - Get amenity details
PUT /api/v1/amenities/{id}/ - Update amenity
DELETE /api/v1/amenities/{id}/ - Delete amenity
Bookings
GET /api/v1/bookings/ - List bookings
POST /api/v1/bookings/ - Create booking
GET /api/v1/bookings/{id}/ - Get booking details
PUT /api/v1/bookings/{id}/ - Update booking
DELETE /api/v1/bookings/{id}/ - Delete booking
GET /api/v1/bookings/calendar/events/ - Calendar events
POST /api/v1/bookings/{id}/soft-delete/ - Soft delete booking
POST /api/v1/bookings/{id}/restore/ - Restore booking
Guests
GET /api/v1/guests/ - List guests
POST /api/v1/guests/ - Create guest
GET /api/v1/guests/{id}/ - Get guest details
PUT /api/v1/guests/{id}/ - Update guest
DELETE /api/v1/guests/{id}/ - Delete guest