# NOV-RECO User Management System

## 👥 User Role Overview

The NOV-RECO system implements a 4-tier user role system with granular permissions:

### 🔴 1. Super Admin
- **Full System Access**: Complete control over all aspects
- **User Management**: Create, edit, delete any user
- **Area Management**: Full CRUD operations on check-in areas
- **Check-in Management**: View, edit, delete all check-ins
- **Admin Panel**: Full Django admin access
- **System Settings**: Configuration and maintenance

### 🟡 2. Quản lý (Manager)
- **User Management**: Add, edit, view users (no delete)
- **Area Management**: Full CRUD operations on check-in areas
- **Check-in Management**: View, edit, delete all check-ins
- **Admin Panel**: Limited admin access
- **Reports**: Access to all reporting features

### 🟢 3. Thư ký (Secretary)
- **User Management**: View users only
- **Area Management**: Add, edit, view areas (no delete)
- **Check-in Management**: Add, edit, view check-ins (no delete)
- **Admin Panel**: Limited admin access
- **Data Entry**: Primary data entry role

### 🔵 4. Nhân viên (Employee)
- **Area Management**: View areas only
- **Check-in Management**: Add and view own check-ins only
- **Profile**: Edit own profile information
- **Mobile Access**: Primary mobile app users

## 🔐 Permission Matrix

| Feature | Super Admin | Manager | Secretary | Employee |
|---------|-------------|---------|-----------|----------|
| **User Management** |
| Create User | ✅ | ✅ | ❌ | ❌ |
| Edit User | ✅ | ✅ | ❌ | Own Only |
| Delete User | ✅ | ❌ | ❌ | ❌ |
| View Users | ✅ | ✅ | ✅ | ❌ |
| **Area Management** |
| Create Area | ✅ | ✅ | ✅ | ❌ |
| Edit Area | ✅ | ✅ | ✅ | ❌ |
| Delete Area | ✅ | ✅ | ❌ | ❌ |
| View Areas | ✅ | ✅ | ✅ | ✅ |
| **Check-in Management** |
| Create Check-in | ✅ | ✅ | ✅ | ✅ |
| Edit Check-in | ✅ | ✅ | ✅ | Own Only |
| Delete Check-in | ✅ | ✅ | ❌ | ❌ |
| View All Check-ins | ✅ | ✅ | ✅ | ❌ |
| View Own Check-ins | ✅ | ✅ | ✅ | ✅ |
| **System Access** |
| Django Admin | ✅ | Limited | Limited | ❌ |
| API Access | ✅ | ✅ | ✅ | Limited |
| Reports | ✅ | ✅ | Limited | Own Only |

## 🎯 Sample User Accounts

### Default Accounts (Created by setup script)

```bash
# Super Admin
Username: superadmin
Password: admin123
Employee ID: SA001
Email: superadmin@reco.local

# Manager
Username: quanly
Password: quanly123
Employee ID: QL001
Email: quanly@reco.local

# Secretary
Username: thuky
Password: thuky123
Employee ID: TK001
Email: thuky@reco.local

# Employee 1
Username: nhanvien1
Password: nhanvien123
Employee ID: NV001
Email: nhanvien1@reco.local

# Employee 2
Username: nhanvien2
Password: nhanvien123
Employee ID: NV002
Email: nhanvien2@reco.local
```

## 🏗️ User Model Structure

### Custom User Fields

```python
class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.EMPLOYEE
    )
    phone = models.CharField(max_length=15, blank=True)
    department = models.CharField(max_length=100, blank=True)
    employee_id = models.CharField(
        max_length=20, 
        blank=True, 
        unique=True
    )
```

### User Roles Enum

```python
class UserRole(models.TextChoices):
    ADMIN = "admin", "Admin"
    MANAGER = "manager", "Quản lý"
    EMPLOYEE = "employee", "Nhân viên"
```

## 🛠️ User Management Commands

### Setup User Groups and Permissions
```bash
python manage.py setup_user_groups
```
- Creates Django Groups for each role
- Assigns appropriate permissions to each group
- Sets up permission inheritance

### Create Sample Users
```bash
python manage.py create_sample_users
```
- Creates 5 sample users (1 per role + extra employee)
- Assigns proper employee IDs
- Adds users to appropriate groups

### Create Admin User
```bash
python manage.py createsuperuser
```
- Creates custom superuser account
- Prompts for username, email, password

## 🎨 Dashboard Views by Role

### Super Admin Dashboard
- **System Overview**: Total users, areas, check-ins
- **Recent Activity**: Latest check-ins across all users
- **User Management**: Quick access to user admin
- **System Health**: Database status, error logs
- **Quick Actions**: Bulk operations, data export

### Manager Dashboard
- **Team Overview**: Department statistics
- **Area Management**: Assigned areas status
- **Check-in Reports**: Team performance metrics
- **User Oversight**: Team member activities
- **Analytics**: Trends and patterns

### Secretary Dashboard
- **Data Entry**: Quick check-in forms
- **Area Status**: Real-time area occupancy
- **User Support**: Help desk functions
- **Document Management**: Forms and reports
- **Calendar**: Scheduled activities

### Employee Dashboard
- **Quick Check-in**: One-click check-in button
- **My History**: Personal check-in history
- **Nearby Areas**: GPS-based area discovery
- **Profile**: Personal information management
- **Help**: User guides and support

## 🔧 Permission Implementation

### Django Groups Integration

```python
# Group Creation
groups = {
    'Super Admin': ['all_permissions'],
    'Quản lý': ['add_user', 'change_user', 'view_user', ...],
    'Thư ký': ['view_user', 'add_area', 'change_area', ...],
    'Nhân viên': ['view_area', 'add_checkin', 'view_checkin']
}
```

### View-Level Permissions

```python
from django.contrib.auth.decorators import permission_required

@permission_required('checkin.add_area')
def create_area(request):
    # Only users with area creation permission
    pass

@permission_required('users.change_user')
def edit_user(request, user_id):
    # Only managers and above
    pass
```

### Template-Level Permissions

```html
{% if perms.checkin.add_area %}
    <a href="{% url 'create_area' %}" class="btn btn-primary">
        Create New Area
    </a>
{% endif %}

{% if user.is_superuser %}
    <div class="admin-panel">
        <!-- Super admin only content -->
    </div>
{% endif %}
```

## 📱 Mobile App Integration

### Role-Based API Endpoints

```python
# Employee endpoints
/api/checkin/create/          # POST - Create check-in
/api/checkin/my-history/      # GET - Own check-ins
/api/areas/nearby/            # GET - Nearby areas

# Manager endpoints  
/api/checkin/all/             # GET - All check-ins
/api/users/team/              # GET - Team members
/api/reports/dashboard/       # GET - Management reports

# Admin endpoints
/api/admin/users/             # CRUD - User management
/api/admin/system/            # GET - System status
```

### Authentication Flow

1. **Login**: POST `/api/auth/login/`
2. **Token**: Receive JWT token with role info
3. **Requests**: Include token in Authorization header
4. **Permissions**: Server validates role for each endpoint

## 🔄 User Lifecycle Management

### User Creation Process
1. **Admin/Manager** creates user account
2. **System** generates employee ID (if not provided)
3. **User** receives welcome email with credentials
4. **First Login** forces password change
5. **Profile Setup** completes onboarding

### Role Changes
1. **Only Super Admin** can change user roles
2. **Permission Update** happens immediately
3. **Session Refresh** required for new permissions
4. **Audit Log** tracks all role changes

### User Deactivation
1. **Soft Delete**: Set `is_active = False`
2. **Data Retention**: Keep check-in history
3. **Access Revoke**: Immediate permission removal
4. **Audit Trail**: Maintain deactivation record

## 📊 Reporting and Analytics

### User Activity Reports
- **Login Frequency**: Track user engagement
- **Check-in Patterns**: Identify usage trends
- **Permission Usage**: Monitor feature adoption
- **Error Rates**: Track user issues

### Role-Based Dashboards
- **Super Admin**: System-wide metrics
- **Manager**: Team performance data
- **Secretary**: Data entry statistics
- **Employee**: Personal activity summary

## 🔒 Security Considerations

### Password Policy
- **Minimum Length**: 8 characters
- **Complexity**: Mix of letters, numbers, symbols
- **Expiration**: Optional 90-day rotation
- **History**: Prevent reuse of last 5 passwords

### Session Management
- **Timeout**: 8 hours for employees, 24 for admin
- **Concurrent Sessions**: Max 3 per user
- **IP Tracking**: Monitor login locations
- **Device Registration**: Track access devices

### Audit Logging
- **User Actions**: All CRUD operations logged
- **Permission Changes**: Role modifications tracked
- **Login Events**: Success and failure attempts
- **Data Access**: Sensitive data viewing logged

## 🚀 Best Practices

### User Management
1. **Principle of Least Privilege**: Grant minimum required permissions
2. **Regular Reviews**: Quarterly permission audits
3. **Onboarding Process**: Standardized user creation
4. **Offboarding Process**: Immediate access revocation

### Role Design
1. **Clear Boundaries**: Well-defined role responsibilities
2. **Scalable Structure**: Easy to add new roles
3. **Business Alignment**: Roles match organizational structure
4. **Documentation**: Clear role descriptions

### Security
1. **Regular Updates**: Keep permissions current
2. **Monitor Access**: Track unusual activity
3. **Training**: User security awareness
4. **Incident Response**: Quick reaction procedures

---

*User Management Documentation for NOV-RECO*
*Last updated: September 19, 2025*
