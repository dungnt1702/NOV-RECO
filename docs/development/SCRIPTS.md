# Scripts Documentation

## 📁 Scripts Directory Structure

```
data/scripts/
├── README.md                    # Scripts overview
├── run.sh                       # Main script manager (macOS/Linux)
├── run.bat                      # Main script manager (Windows)
├── quick_start_mac.sh           # Quick start (macOS/Linux)
├── quick_start_windows.bat      # Quick start (Windows)
├── setup_complete_data.sh       # Complete data setup (macOS/Linux)
├── setup_complete_data.bat      # Complete data setup (Windows)
├── start_reco_local.sh          # Start with browser (macOS/Linux)
├── start_reco_local.bat         # Start with browser (Windows)
├── start_server.sh              # Start server only (macOS/Linux)
├── run_server.py                # Python server script
├── start_server.py              # Advanced Python server script
└── create_sample_users.py       # Sample data creation
```

## 🚀 Quick Start

### Using Script Manager (Recommended)

**macOS/Linux:**
```bash
./data/scripts/run.sh
```

**Windows:**
```cmd
data\scripts\run.bat
```

### Direct Execution

**macOS/Linux:**
```bash
./data/scripts/quick_start_mac.sh
```

**Windows:**
```cmd
data\scripts\quick_start_windows.bat
```

## 📋 Script Descriptions

### 1. Script Managers
- **`run.sh`** / **`run.bat`**: Interactive menu to choose and run scripts
- Features: Menu-driven interface, cross-platform support

### 2. Quick Start Scripts
- **`quick_start_mac.sh`** / **`quick_start_windows.bat`**
- **Purpose**: Complete system startup
- **Features**:
  - Stop existing servers
  - Install/upgrade dependencies
  - Run database migrations
  - Collect static files
  - Create admin user if needed
  - Start development server

### 3. Data Setup Scripts
- **`setup_complete_data.sh`** / **`setup_complete_data.bat`**
- **Purpose**: Set up complete sample data
- **Features**:
  - Create user groups and permissions
  - Generate sample users
  - Create sample areas
  - Display login credentials

### 4. Server Scripts
- **`start_server.sh`**: Simple server startup (macOS/Linux)
- **`run_server.py`**: Python-based server startup
- **`start_server.py`**: Advanced Python server with auto-setup
- **`start_reco_local.sh`** / **`start_reco_local.bat`**: Start server and open browser

## 🔧 Configuration

### Default Settings
- **Port**: 3000
- **Host**: 127.0.0.1 (localhost)
- **Database**: SQLite (db.sqlite3)
- **Static Files**: Automatically collected

### Environment Variables
Scripts automatically handle:
- Virtual environment activation
- Python path setup
- Django settings configuration

## 🎯 Usage Examples

### Development Workflow
```bash
# 1. Start development environment
./data/scripts/quick_start_mac.sh

# 2. Setup sample data (if needed)
./data/scripts/setup_complete_data.sh

# 3. Start with browser
./data/scripts/start_reco_local.sh
```

### Production Deployment
```bash
# 1. Setup complete environment
./data/scripts/setup_complete_data.sh

# 2. Start production server
python data/scripts/start_server.py
```

### Troubleshooting
```bash
# 1. Reset everything
./data/scripts/quick_start_mac.sh

# 2. Check server status
python manage.py check

# 3. View database
python manage.py view_database
```

## 🔍 Script Features

### Error Handling
- Automatic process cleanup
- Port conflict resolution
- Dependency checking
- Graceful error messages

### Cross-Platform Support
- macOS/Linux: Bash scripts with color output
- Windows: Batch scripts with proper encoding
- Python: Universal scripts for all platforms

### Automation
- Automatic server stopping/starting
- Dependency installation
- Database migration
- Static file collection
- Admin user creation

## 📊 Default Credentials

After running `setup_complete_data`:

| Role | Username | Password | Permissions |
|------|----------|----------|-------------|
| Super Admin | `superadmin` | `admin123` | Full system access |
| Manager | `quanly` | `quanly123` | Team management |
| Secretary | `thuky` | `thuky123` | View and edit (except users) |
| Employee 1 | `nhanvien1` | `nhanvien123` | Check-in only |
| Employee 2 | `nhanvien2` | `nhanvien123` | Check-in only |

## 🌐 Access URLs

- **Homepage**: http://localhost:3000
- **Admin Panel**: http://localhost:3000/admin
- **API Root**: http://localhost:3000/api/

## ⚠️ Troubleshooting

### Common Issues

**Port Already in Use:**
```bash
# Scripts automatically handle this, but manual fix:
pkill -f "python manage.py runserver"
```

**Permission Denied:**
```bash
# Make scripts executable
chmod +x data/scripts/*.sh
```

**Database Locked:**
```bash
# Reset database
rm db.sqlite3
python manage.py migrate
```

**Dependencies Missing:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Script Debugging
```bash
# Run with verbose output
bash -x ./data/scripts/quick_start_mac.sh

# Check script syntax
bash -n ./data/scripts/quick_start_mac.sh
```

## 🔄 Maintenance

### Regular Tasks
1. **Update Dependencies**: Scripts automatically upgrade packages
2. **Database Backup**: Manual backup before major changes
3. **Log Cleanup**: Clear old log files periodically
4. **Static Files**: Recollect after template changes

### Script Updates
- Scripts are version-controlled with the project
- Update scripts when adding new features
- Test scripts on both platforms before committing
