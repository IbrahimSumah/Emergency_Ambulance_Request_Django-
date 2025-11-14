# Emergency Ambulance Request System

A modern Django-based emergency ambulance dispatch system with real-time WebSocket capabilities, built with ASGI for full asynchronous support.

## 🚨 Features

- **Real-time Emergency Call Management**: Create and manage emergency calls with real-time updates via WebSockets
- **Dispatcher Dashboard**: Live dashboard for dispatchers to monitor and assign ambulances
- **Paramedic Interface**: Mobile-friendly interface for paramedics to update emergency status
- **Ambulance Fleet Management**: Track and manage ambulance fleet with location updates
- **Hospital Capacity Management**: Monitor hospital capacity and availability
- **Image Upload**: Emergency situation image upload and management
- **Real-time Notifications**: WebSocket-based real-time notifications for all stakeholders
- **REST API**: Comprehensive REST API for integration

## 🛠️ Technology Stack

- **Backend**: Django 5.2+ with ASGI (Asynchronous Server Gateway Interface)
- **Server**: Daphne (ASGI server) for production deployment
- **WebSockets**: Django Channels for real-time communication
- **Channel Layer**: Redis (with InMemory fallback for development)
- **API**: Django REST Framework
- **Static Files**: WhiteNoise for static file serving
- **Database**: SQLite (development) / PostgreSQL (production)

## 📋 Prerequisites

- Python 3.11+
- Redis Server (optional - system falls back to InMemory for development)
- PostgreSQL (optional - SQLite included for development)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Emergency_Ambulance_Request_Django-
```

### 2. Create Virtual Environment

```bash
python -m venv space
source space/bin/activate  # Linux/Mac
# or
space\Scripts\activate     # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Database

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Start the Server

#### Development (Basic Testing)
```bash
python manage.py runserver
```

#### Production-like with ASGI (Full Features)
```bash
# Start Redis server (optional but recommended)
redis-server

# Start ASGI server with Daphne
daphne -b 0.0.0.0 -p 8000 EmmergencyAmbulanceSystem.asgi:application
```

#### Docker Deployment
```bash
docker-compose up -d
```

## 🏗️ ASGI Deployment

This application uses **ASGI (Asynchronous Server Gateway Interface)** instead of WSGI for full WebSocket and asynchronous support.

### Why ASGI?

- **WebSocket Support**: Full WebSocket protocol support for real-time communication
- **Async Capabilities**: Support for async views and middleware
- **Modern Standards**: Aligned with modern Python async/await patterns
- **Better Performance**: Improved performance for concurrent connections

### ASGI Configuration

The application is configured to use:
- **ASGI Server**: Daphne (recommended) or Uvicorn
- **ASGI Application**: `EmmergencyAmbulanceSystem.asgi:application`
- **WebSocket Routing**: Configured via Django Channels
- **Channel Layer**: Redis for production, InMemory for development fallback

### Running with ASGI

**Using Daphne (Recommended)**:
```bash
daphne -b 0.0.0.0 -p 8000 EmmergencyAmbulanceSystem.asgi:application
```

**Using Uvicorn (Alternative)**:
```bash
uvicorn EmmergencyAmbulanceSystem.asgi:application --host 0.0.0.0 --port 8000
```

**NOT Compatible**: 
- ❌ Gunicorn (WSGI server - not compatible with ASGI)
- ❌ Apache mod_wsgi (WSGI only)

### WebSocket Endpoints

- **Dispatcher WebSocket**: `ws://localhost:8000/ws/dispatchers/`
- **Paramedic WebSocket**: `ws://localhost:8000/ws/paramedic/`

## 📁 Project Structure

```
Emergency_Ambulance_Request_Django-/
├── core/                    # Core user management and utilities
├── emergencies/             # Emergency call management and WebSocket consumers
├── dispatch/                # Ambulance and hospital dispatch management
├── profiles/                # User profile management
├── EmmergencyAmbulanceSystem/  # Main project settings and ASGI configuration
├── templates/               # HTML templates
├── static/                  # Static files (CSS, JS)
├── media/                   # User-uploaded files
├── docs/                    # Documentation
└── requirements.txt         # Python dependencies
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=sqlite:///db.sqlite3
```

### Required Packages

Key packages installed via `requirements.txt`:
- `django` - Django framework
- `daphne` - ASGI server
- `channels` - WebSocket support
- `channels-redis` - Redis channel layer
- `djangorestframework` - REST API
- `whitenoise` - Static file serving
- `django-cors-headers` - CORS support

## 📚 Documentation

- **Setup Guide**: See [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) for detailed setup instructions
- **Migration Guide**: See [MIGRATION_WSGI_TO_ASGI.md](MIGRATION_WSGI_TO_ASGI.md) for WSGI to ASGI migration details
- **System Design**: See [docs/System_Workflow_Design.md](docs/System_Workflow_Design.md) for system architecture

## 🌐 API Endpoints

### Emergency Calls
- `GET/POST /api/emergencies/` - List/create emergency calls
- `GET/PATCH /api/emergencies/{id}/` - Retrieve/update emergency call

### Dispatch
- `GET/POST /api/ambulances/` - Ambulance fleet management
- `GET/POST /api/hospitals/` - Hospital management
- `POST /api/dispatch/assign/` - Assign ambulance to emergency

### WebSocket
- `ws://localhost:8000/ws/dispatchers/` - Dispatcher real-time updates
- `ws://localhost:8000/ws/paramedic/` - Paramedic real-time updates

## 🧪 Testing

```bash
# Run tests
python manage.py test

# Run with pytest
pytest
```

## 🚀 Production Deployment

### Environment Setup

```env
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
REDIS_URL=redis://redis-host:6379/0
DATABASE_URL=postgres://user:pass@host:5432/dbname
```

### Deployment Steps

1. Set production environment variables
2. Run migrations: `python manage.py migrate`
3. Collect static files: `python manage.py collectstatic`
4. Start ASGI server with Daphne or Uvicorn
5. Configure reverse proxy (nginx) for static files and SSL
6. Ensure Redis is running for WebSocket functionality

### Production Requirements

- **ASGI Server**: Daphne or Uvicorn (NOT Gunicorn)
- **Redis**: Required for production WebSocket functionality
- **Database**: PostgreSQL recommended for production
- **Static Files**: WhiteNoise or nginx for static file serving
- **HTTPS**: SSL/TLS certificate for secure WebSocket connections

## 📝 License

[Add your license here]

## 👥 Contributing

[Add contributing guidelines here]

## 🆘 Support

For detailed setup instructions and troubleshooting, see [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)

## 📄 Notes

- This project has been migrated from WSGI to ASGI for full WebSocket support
- The development server (`runserver`) works for basic testing but doesn't support all WebSocket features
- For production, use Daphne or Uvicorn ASGI servers
- Redis is recommended but not required (system falls back to InMemory for development)
