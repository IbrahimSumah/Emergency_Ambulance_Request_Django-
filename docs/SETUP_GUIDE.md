# Emergency Ambulance System - Setup Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 16+ (for frontend assets)
- Redis Server (optional - system falls back to InMemory)
- PostgreSQL (optional - SQLite included)

### 1. Environment Setup

```bash
# Clone and navigate to project
cd EmmergencyAmbulanceSystem

# Create virtual environment
python -m venv space
source space/bin/activate  # Linux/Mac
# or
space\Scripts\activate     # Windows

# Install dependencies (already done)
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
# Minimum required:
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample data (optional)
python manage.py loaddata fixtures/sample_data.json
```

### 4. Start Services

#### Option A: Development (Current Setup)
```bash
# Start Django development server
python manage.py runserver
```

#### Option B: With Redis (Full Features)
```bash
# Start Redis server
redis-server

# Start Django with WebSocket support
python manage.py runserver
```

#### Option C: Docker (Production-like)
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f web
```

## 🔧 Core Functionality Setup

### User Management
1. **Create Initial Users**:
   ```bash
   python manage.py shell
   ```
   ```python
   from core.models import User
   
   # Create dispatcher
   dispatcher = User.objects.create_user(
       username='dispatcher1',
       email='dispatcher@emergency.com',
       password='secure_password',
       first_name='John',
       last_name='Dispatcher',
       role='dispatcher'
   )
   
   # Create paramedic
   paramedic = User.objects.create_user(
       username='paramedic1',
       email='paramedic@emergency.com',
       password='secure_password',
       first_name='Jane',
       last_name='Paramedic',
       role='paramedic'
   )
   ```

### Fleet Setup
2. **Add Ambulances**:
   ```python
   from dispatch.models import Ambulance, Hospital
   
   # Create hospital
   hospital = Hospital.objects.create(
       name='General Hospital',
       address='123 Medical Center Dr',
       latitude=40.7128,
       longitude=-74.0060,
       phone='555-0123'
   )
   
   # Create ambulance
   ambulance = Ambulance.objects.create(
       unit_number='AMB-001',
       status='AVAILABLE',
       base_station='Station 1',
       assigned_paramedic=paramedic
   )
   ```

## 📋 System URLs & Access Points

### Public Access
- **Emergency Request Form**: `http://localhost:8000/emergency/`
- **System Status**: `http://localhost:8000/`

### Authenticated Access
- **Login**: `http://localhost:8000/login/`
- **Dispatcher Dashboard**: `http://localhost:8000/dashboard/`
- **Paramedic Interface**: `http://localhost:8000/paramedic/`
- **Admin Panel**: `http://localhost:8000/admin/`

### API Endpoints
- **Emergency Calls**: `http://localhost:8000/api/emergencies/`
- **Ambulance Fleet**: `http://localhost:8000/api/ambulances/`
- **Image Upload**: `http://localhost:8000/api/upload-image/`

## 🔍 Testing Core Features

### 1. Emergency Call Flow
1. Visit emergency form: `http://localhost:8000/emergency/`
2. Fill out emergency details
3. Submit request
4. Check dispatcher dashboard for new call
5. Assign ambulance via drag-drop
6. Use paramedic interface to update status

### 2. Real-time Features (with Redis)
1. Open dispatcher dashboard in multiple tabs
2. Create emergency call in one tab
3. Verify real-time updates in other tabs
4. Test WebSocket connectivity

### 3. File Upload
1. Test emergency image upload
2. Verify files saved to `media/emergency_images/`
3. Check image display in call details

## ⚠️ Common Issues & Solutions

### Redis Connection Issues
**Problem**: `ConnectionRefusedError: [WinError 1225]`
**Solution**: System automatically falls back to InMemoryChannelLayer
```python
# Verify fallback in settings.py
if test_redis_connection():
    # Uses Redis
else:
    # Uses InMemory (current setup)
```

### Migration Conflicts
**Problem**: `Conflicting migrations detected`
**Solution**: 
```bash
python manage.py makemigrations --merge
python manage.py migrate
```

### Static Files Not Loading
**Problem**: CSS/JS not loading
**Solution**:
```bash
python manage.py collectstatic
# Ensure STATIC_URL and STATICFILES_DIRS are configured
```

### WebSocket Connection Failed
**Problem**: Real-time features not working
**Solution**: Check channel layer configuration and Redis status

## 🚀 Production Deployment

### Environment Variables
```bash
# Production settings
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgres://user:pass@host:5432/dbname
REDIS_URL=redis://redis-host:6379/0
```

### Docker Deployment
```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d

# SSL with Let's Encrypt
certbot --nginx -d yourdomain.com
```

### Performance Optimization
- Enable Redis for production
- Use PostgreSQL instead of SQLite
- Configure nginx for static files
- Set up proper logging
- Enable HTTPS

## 📊 Monitoring & Maintenance

### Health Checks
- Database connectivity: `/admin/`
- Redis status: Check WebSocket features
- File uploads: Test image upload
- API endpoints: Test emergency creation

### Regular Maintenance
```bash
# Clear old emergency calls (optional)
python manage.py shell -c "
from emergencies.models import EmergencyCall
from datetime import datetime, timedelta
old_calls = EmergencyCall.objects.filter(
    status='CLOSED',
    closed_at__lt=datetime.now() - timedelta(days=30)
)
print(f'Cleaning up {old_calls.count()} old calls')
old_calls.delete()
"

# Backup database
python manage.py dumpdata > backup_$(date +%Y%m%d).json
```

## 🆘 Support & Troubleshooting

### Log Locations
- Django logs: Console output
- Redis logs: `/var/log/redis/`
- Nginx logs: `/var/log/nginx/`

### Debug Mode
```python
# Enable detailed error pages
DEBUG = True

# Enable SQL query logging
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### Performance Monitoring
- Monitor response times
- Check database query efficiency
- Monitor WebSocket connections
- Track file upload sizes
