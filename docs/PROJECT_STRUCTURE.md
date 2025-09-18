# NOV-RECO Project Structure

## 📁 Cấu trúc thư mục

```
checkin.reco.vn/
├── 📁 checkin/                    # Django app chính
│   ├── 📁 management/
│   │   └── 📁 commands/           # Management commands
│   │       ├── create_admin.py
│   │       ├── create_sample_areas.py
│   │       ├── create_sample_users.py
│   │       ├── setup_user_groups.py
│   │       └── ...
│   ├── 📁 migrations/             # Database migrations
│   ├── admin.py                   # Django admin configuration
│   ├── models.py                  # Database models
│   ├── views.py                   # View functions
│   └── urls.py                    # URL routing
│
├── 📁 users/                      # User management app
│   ├── 📁 migrations/
│   ├── models.py                  # Custom User model
│   ├── forms.py                   # User forms
│   ├── views.py                   # User management views
│   └── ...
│
├── 📁 project/                    # Django project settings
│   ├── settings.py                # Main settings
│   ├── urls.py                    # Root URL configuration
│   └── wsgi.py                    # WSGI configuration
│
├── 📁 templates/                  # HTML templates
│   ├── 📁 base.html               # Base template
│   ├── 📁 checkin/                # Check-in templates
│   ├── 📁 account/                # Authentication templates
│   └── 📁 users/                  # User management templates
│
├── 📁 static/                     # Static files (CSS, JS, images)
│   ├── 📁 css/                    # Stylesheets
│   ├── 📁 js/                     # JavaScript files
│   └── 📁 favicon.png, logo.svg
│
├── 📁 staticfiles/                # Collected static files (auto-generated)
│
├── 📁 data/                       # 🆕 Data & Configuration folder
│   ├── 📁 scripts/                # Setup and utility scripts
│   │   ├── setup_complete_data.bat    # Complete data setup
│   │   ├── start_reco_local.bat       # Start local server
│   │   └── create_sample_users.py     # Legacy script
│   └── db.sqlite3                 # SQLite database
│
├── 📁 docs/                       # Documentation
│   ├── INDEX.md                   # Documentation index
│   ├── PROJECT_STRUCTURE.md       # This file
│   ├── INSTALLATION.md            # Installation guide
│   ├── USER_MANAGEMENT.md         # User roles documentation
│   └── API_DOCUMENTATION.md       # API documentation
│
├── manage.py                      # Django management script
├── requirements.txt               # Python dependencies
└── README.md                      # Main project documentation
```

## 🔧 Core Components

### 1. **Django Apps**

#### **checkin/** - Main Application
- **Purpose**: Core check-in functionality
- **Key Models**: `Area`, `Checkin`, `Location`
- **Features**: GPS-based check-in, area management, history tracking

#### **users/** - User Management
- **Purpose**: Custom user model and authentication
- **Key Models**: `User` with roles (admin, manager, employee)
- **Features**: Role-based permissions, employee ID management

#### **project/** - Django Project
- **Purpose**: Main project configuration
- **Key Files**: `settings.py`, `urls.py`, `wsgi.py`

### 2. **Frontend Structure**

#### **templates/** - HTML Templates
```
templates/
├── base.html                      # Base layout with navigation
├── home.html                      # Landing page
├── checkin/
│   ├── checkin.html              # Check-in form
│   ├── checkin_success.html      # Success page
│   ├── admin_dashboard.html      # Admin dashboard
│   ├── manager_dashboard.html    # Manager dashboard
│   ├── employee_dashboard.html   # Employee dashboard
│   └── user_history.html         # Check-in history
├── account/
│   ├── login.html                # Login form
│   ├── signup.html               # Registration form
│   └── password_reset.html       # Password reset
└── users/
    ├── user_list.html            # User management
    ├── user_form.html            # User create/edit
    └── user_confirm_delete.html  # User deletion
```

#### **static/** - Static Assets
```
static/
├── css/
│   ├── base.css                  # Base styles
│   ├── checkin.css               # Check-in specific styles
│   ├── dashboard.css             # Dashboard styles
│   ├── auth.css                  # Authentication styles
│   └── users.css                 # User management styles
├── js/
│   ├── base.js                   # Base JavaScript
│   ├── checkin.js                # Check-in functionality
│   ├── auth.js                   # Authentication handling
│   └── users.js                  # User management JS
└── logo.svg, favicon.png         # Branding assets
```

### 3. **Data Management**

#### **data/** - Data & Configuration
- **📁 scripts/**: Setup and utility scripts
- **db.sqlite3**: SQLite database file
- **Purpose**: Centralized data storage and configuration

#### **Management Commands**
- `setup_user_groups`: Create user groups and permissions
- `create_sample_users`: Generate sample users for testing
- `create_sample_areas`: Create sample check-in areas
- `create_admin`: Create admin user

### 4. **Documentation**

#### **docs/** - Project Documentation
- Comprehensive guides for installation, usage, and development
- API documentation and troubleshooting guides
- Architecture and design decisions

## 🚀 Key Features

### **Authentication & Authorization**
- Custom User model with employee ID
- Role-based access control (4 levels)
- Django Groups and Permissions integration

### **Check-in System**
- GPS-based location verification
- Area management with radius validation
- Photo capture and storage
- History tracking and reporting

### **User Interface**
- Responsive design for mobile and desktop
- Role-specific dashboards
- Real-time location services
- Camera integration

### **Data Management**
- SQLite database (development)
- Automated data setup scripts
- Sample data for testing
- Migration management

## 🔄 Development Workflow

1. **Setup**: Run `data/scripts/setup_complete_data.bat`
2. **Development**: Use `data/scripts/start_reco_local.bat`
3. **Testing**: Access different user roles with sample accounts
4. **Deployment**: Follow deployment guides in docs/

## 📊 Database Schema

### **Key Models**

#### **users.User**
- Extended Django User with custom fields
- Roles: admin, manager, employee
- Employee ID and department tracking

#### **checkin.Area**
- GPS coordinates with radius
- Created by admin/manager users
- Active/inactive status

#### **checkin.Checkin**
- User check-in records
- GPS coordinates and validation
- Photo evidence and notes
- Timestamp and IP tracking

## 🔗 Integration Points

- **Django Admin**: Full administrative interface
- **REST API**: For mobile app integration
- **Static Files**: Efficient asset serving
- **Media Files**: Photo storage and retrieval
- **Virtual Host**: Professional domain setup (reco.local)

---

*Last updated: September 19, 2025*
*Version: 1.0.0*
