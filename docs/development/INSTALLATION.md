# Installation Guide

## 📋 Requirements

- Python 3.8+
- Django 4.2+
- SQLite (default)
- Modern web browser

## 🚀 Installation Steps

### 1. Clone Repository
```bash
git clone <repository-url>
cd checkin_project
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Database Setup
```bash
python manage.py migrate
```

### 4. Create Admin User
```bash
python manage.py create_admin
```

### 5. Collect Static Files
```bash
python manage.py collectstatic
```

### 6. Start Server
```bash
python manage.py runserver 127.0.0.1:3000
```

## 🔧 Configuration

### Environment Variables
Create `.env` file:
```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3
```

### Google Maps API (Optional)
Add to `settings.py`:
```python
GOOGLE_MAPS_API_KEY = "your-api-key"
```

## 🐳 Docker (Optional)

```bash
docker build -t nov-reco-checkin .
docker run -p 3000:3000 nov-reco-checkin
```

## 🔍 Troubleshooting

### Port Already in Use
```bash
# Kill existing process
pkill -f "python manage.py runserver"

# Or use different port
python manage.py runserver 127.0.0.1:8000
```

### Database Issues
```bash
# Reset database
rm db.sqlite3
python manage.py migrate
python manage.py create_admin
```

### Static Files Issues
```bash
python manage.py collectstatic --clear
```
