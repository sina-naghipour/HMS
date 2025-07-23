templates/
├── admin/
│   ├── base.html                # Base template
│   ├── dashboard.html           # Main dashboard
│   ├── includes/
│   │   ├── sidebar.html         # Navigation sidebar
│   │   ├── navbar.html          # Top navigation bar
│   │   ├── footer.html          # Footer
│   │   ├── messages.html        # Notification messages
│   │   └── breadcrumb.html      # Breadcrumb navigation
│   ├── bookings/
│   │   ├── list.html            # All bookings
│   │   ├── detail.html          # Booking details
│   │   ├── create.html          # Create new booking
│   │   └── calendar.html        # Booking calendar view
│   ├── rooms/
│   │   ├── list.html            # All rooms
│   │   ├── detail.html          # Room details
│   │   ├── create.html          # Add new room
│   │   └── types/               # Room types
│   │       ├── list.html
│   │       └── detail.html
│   ├── guests/
│   │   ├── list.html            # All guests
│   │   ├── detail.html          # Guest profile
│   │   └── create.html          # Add new guest
│   ├── staff/
│   │   ├── list.html            # Staff members
│   │   └── detail.html          # Staff details
│   ├── reports/
│   │   ├── occupancy.html       # Occupancy reports
│   │   ├── revenue.html         # Revenue reports
│   │   └── custom.html          # Custom reports
│   ├── services/
│   │   ├── list.html            # Additional services
│   │   └── detail.html          # Service details
│   └── settings/
│       ├── general.html         # General settings
│       ├── payment.html         # Payment settings
│       └── email.html           # Email settings
├── registration/
│   ├── login.html               # Login page
│   └── register.html            # Register page
└── base.html                    # Main base template