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

#### Option A: Development Server (Recommended for Development)
```bash
# Start Django development server (supports ASGI and WebSockets)
python manage.py runserver
```

#### Option B: ASGI Server with Redis (Full Features - Recommended)
```bash
# Start Redis server (required for WebSocket functionality)
redis-server

# Start ASGI server with Daphne (supports WebSockets and HTTP)
daphne -b 0.0.0.0 -p 8000 EmmergencyAmbulanceSystem.asgi:application
```

#### Option C: Docker (Production-like)
```bash
# Start all services (uses Daphne ASGI server)
docker-compose up -d

# View logs
docker-compose logs -f web
```

**Important**: This application uses **ASGI (Asynchronous Server Gateway Interface)** for full WebSocket support. 
The development server (`runserver`) works for basic testing, but for production and full WebSocket functionality, 
use **Daphne** or **Uvicorn** ASGI servers.

**ASGI Configuration**:
- **Application Entry Point**: `EmmergencyAmbulanceSystem.asgi:application`
- **Recommended Server**: Daphne (included in requirements.txt)
- **Alternative Server**: Uvicorn
- **NOT Compatible**: Gunicorn (WSGI server - use Daphne or Uvicorn instead)

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
**Solution**: 
- Ensure you're using an ASGI server (Daphne or Uvicorn), not the development server
- Check Redis server is running (if using Redis channel layer)
- Verify WebSocket endpoint URLs are correct
- Check browser console for connection errors
- Ensure ASGI application is properly configured in `asgi.py`

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
# Build and deploy (uses Daphne ASGI server)
docker-compose up -d

# View logs
docker-compose logs -f web

# For production with SSL
docker-compose -f docker-compose.prod.yml up -d
certbot --nginx -d yourdomain.com
```

**Note**: The Docker configuration uses Daphne ASGI server. Ensure your `docker-compose.yml` 
or `docker-compose.prod.yml` is configured to use:
```yaml
command: daphne -b 0.0.0.0 -p 8000 EmmergencyAmbulanceSystem.asgi:application
```

### Performance Optimization
- **Enable Redis for production**: Required for WebSocket functionality at scale
- **Use PostgreSQL instead of SQLite**: Better performance and reliability
- **Configure nginx for static files**: Reverse proxy for static file serving
- **Use ASGI server**: Daphne or Uvicorn for production (NOT Gunicorn)
- **Set up proper logging**: Monitor application performance
- **Enable HTTPS**: Required for secure WebSocket connections (wss://)
- **Configure connection pooling**: Optimize database and Redis connections

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
