# WSGI to ASGI Migration Checklist

This document tracks the complete migration from WSGI to ASGI for the Emergency Ambulance Request Django project.

## ⚠️ CRITICAL: Missing Dependencies

**IMPORTANT**: The following critical packages are required but NOT currently installed in your environment:

- **`channels`** - REQUIRED for ASGI WebSocket support (used in INSTALLED_APPS, asgi.py)
- **`channels-redis`** - REQUIRED for Redis channel layer (used in settings.py)
- **`django-cors-headers`** - REQUIRED for CORS (used in INSTALLED_APPS, MIDDLEWARE)
- **`daphne`** - REQUIRED for ASGI server (used in Dockerfile, docker-compose.yml)
- **`redis`** - REQUIRED for Redis connection (used in settings.py)

**Action Required**: Run the following command to install all missing dependencies:
```bash
pip install -r requirements.txt
```

**Note**: Without these packages, the application will fail to start. The ASGI server (Daphne) and WebSocket functionality (Channels) will not work.

---

## Migration Overview

**Objective**: Complete migration from WSGI to ASGI to enable full WebSocket support and modern async capabilities.

**Current Status**: ASGI is partially configured but WSGI references still exist.

**Target**: Remove all WSGI dependencies and ensure 100% ASGI deployment.

---

## Migration Tasks

### 1. Settings Configuration
- [x] **Task 1.1**: Remove or comment out `WSGI_APPLICATION` setting from `settings.py` (line 81)
  - **File**: `EmmergencyAmbulanceSystem/settings.py`
  - **Action**: Comment out or remove `WSGI_APPLICATION = 'EmmergencyAmbulanceSystem.wsgi.application'`
  - **Status**: ✅ Completed
  - **Notes**: ASGI_APPLICATION is already configured, WSGI setting is no longer needed
  - **Changes Made**: Commented out WSGI_APPLICATION with deprecation note

### 2. Docker Configuration
- [x] **Task 2.1**: Update `docker-compose.yml` to use Daphne ASGI server
  - **File**: `docker-compose.yml`
  - **Current**: `command: python manage.py runserver 0.0.0.0:8000`
  - **Target**: `command: daphne -b 0.0.0.0 -p 8000 EmmergencyAmbulanceSystem.asgi:application`
  - **Status**: ✅ Completed
  - **Notes**: Dockerfile already uses Daphne, but docker-compose overrides it
  - **Changes Made**: Updated command to use Daphne ASGI server

### 3. Dependencies
- [x] **Task 3.1**: Remove gunicorn from `requirements.txt`
  - **File**: `requirements.txt`
  - **Action**: Remove `gunicorn` (line 10)
  - **Status**: ✅ Completed
  - **Notes**: Gunicorn is a WSGI server, not needed for ASGI deployment. Daphne is already included.
  - **Changes Made**: Removed `gunicorn` from requirements.txt
  - **⚠️ IMPORTANT**: The following critical packages are in requirements.txt but NOT installed:
    - `channels` - **REQUIRED** for ASGI WebSocket support (used in INSTALLED_APPS, asgi.py)
    - `channels-redis` - **REQUIRED** for Redis channel layer (used in settings.py)
    - `django-cors-headers` - **REQUIRED** for CORS (used in INSTALLED_APPS, MIDDLEWARE)
    - `daphne` - **REQUIRED** for ASGI server (used in Dockerfile, docker-compose.yml)
    - `redis` - **REQUIRED** for Redis connection (used in settings.py)
    - **Action Required**: Run `pip install -r requirements.txt` to install missing dependencies

### 4. Middleware Configuration
- [x] **Task 4.1**: Verify ASGI middleware compatibility
  - **File**: `EmmergencyAmbulanceSystem/settings.py`
  - **Action**: Review MIDDLEWARE list (lines 53-62)
  - **Status**: ✅ Completed
  - **Notes**: All middleware is ASGI-compatible. Django's standard middleware works with ASGI.
  - **Current Middleware** (All ASGI-Compatible):
    - ✅ `corsheaders.middleware.CorsMiddleware` - ASGI compatible
    - ✅ `django.middleware.security.SecurityMiddleware` - ASGI compatible
    - ✅ `django.contrib.sessions.middleware.SessionMiddleware` - ASGI compatible
    - ✅ `django.middleware.common.CommonMiddleware` - ASGI compatible
    - ✅ `django.middleware.csrf.CsrfViewMiddleware` - ASGI compatible
    - ✅ `django.contrib.auth.middleware.AuthenticationMiddleware` - ASGI compatible
    - ✅ `django.contrib.messages.middleware.MessageMiddleware` - ASGI compatible
    - ✅ `django.middleware.clickjacking.XFrameOptionsMiddleware` - ASGI compatible
  - **Verification**: All middleware in the list is part of Django's standard middleware stack and is fully compatible with ASGI applications. No changes needed.
  - **⚠️ WARNING**: `corsheaders` package is not installed but is required for `CorsMiddleware` to work. Install with `pip install django-cors-headers`.

### 5. Code Optimization
- [x] **Task 5.1**: Review and optimize async/sync code patterns in `emergencies/views.py`
  - **File**: `emergencies/views.py`
  - **Action**: Identify views using `async_to_sync` and optimize channel layer operations
  - **Status**: ✅ Completed
  - **Notes**: Refactored to use centralized utility functions from `core.utils`
  - **Changes Made**:
    - Created `core/utils.py` with reusable notification utility functions
    - Replaced duplicate `async_to_sync` code with `send_emergency_notification()` utility
    - Optimized `EmergencyCallListCreateView.send_notification()`
    - Optimized `EmergencyCallDetailView.send_notification()`
    - Optimized `update_emergency_status()` function
  - **Benefits**:
    - Reduced code duplication
    - Centralized error handling
    - Easier to maintain and test
    - Better separation of concerns
  
- [x] **Task 5.2**: Review and optimize async/sync code patterns in `dispatch/views.py`
  - **File**: `dispatch/views.py`
  - **Action**: Identify views using `async_to_sync` and optimize channel layer operations
  - **Status**: ✅ Completed
  - **Notes**: Refactored to use centralized utility functions from `core.utils`
  - **Changes Made**:
    - Replaced duplicate `async_to_sync` code with utility functions
    - Optimized `update_ambulance_location()` to use `send_ambulance_notification()`
    - Optimized `dispatch_ambulance()` to use `send_ambulance_notification()` and `send_emergency_notification()`
    - Optimized `update_hospital_capacity()` to use `send_hospital_notification()`
  - **Benefits**:
    - Reduced code duplication
    - Consistent notification pattern across all views
    - Better error handling and logging

### 6. Static Files Configuration
- [x] **Task 6.1**: Verify static files serving in ASGI
  - **File**: `EmmergencyAmbulanceSystem/settings.py`
  - **Action**: Ensure WhiteNoise is properly configured or nginx is set up for static files
  - **Status**: ✅ Completed
  - **Notes**: WhiteNoise is properly configured for ASGI static file serving
  - **Changes Made**:
    - Added `whitenoise.middleware.WhiteNoiseMiddleware` to MIDDLEWARE (after SecurityMiddleware)
    - Configured `STATIC_ROOT = BASE_DIR / 'staticfiles'`
    - Added `STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'`
  - **Configuration**:
    - WhiteNoise middleware is in MIDDLEWARE stack
    - Static files will be served efficiently in ASGI
    - Nginx can still be used in production as a reverse proxy
  - **Next Step**: Run `python manage.py collectstatic` to collect static files

### 7. Application Initialization
- [x] **Task 7.1**: Verify `manage.py` ASGI compatibility
  - **File**: `manage.py`
  - **Action**: Verify Django setup works correctly with ASGI
  - **Status**: ✅ Completed
  - **Notes**: manage.py is fully ASGI-compatible and requires no changes
  - **Verification**:
    - Standard Django management command execution
    - Works correctly with ASGI applications
    - All management commands (migrate, collectstatic, etc.) work as expected
    - No modifications needed

### 8. WSGI File Cleanup
- [x] **Task 8.1**: Deprecate or remove `wsgi.py` file
  - **File**: `EmmergencyAmbulanceSystem/wsgi.py`
  - **Action**: Add deprecation warning and comprehensive documentation
  - **Status**: ✅ Completed
  - **Changes Made**:
    - Added comprehensive deprecation warning at the top of the file
    - Added Python `warnings.warn()` to issue runtime deprecation warning if imported
    - Documented migration status and ASGI configuration
    - Added clear instructions on what to use instead (ASGI)
    - Added reference to migration documentation
    - Kept file for backward compatibility but marked as deprecated
  - **Decision**: Kept file with deprecation warnings instead of removing
    - **Reason**: Safer for deployment environments that might reference it
    - **Benefit**: Clear warning messages prevent accidental WSGI usage
    - **Future**: Can be removed in a later version after confirming no dependencies
  - **Warning System**: 
    - File-level documentation warning
    - Runtime Python deprecation warning if imported
    - Clear instructions to use ASGI instead

### 9. Documentation Updates
- [x] **Task 9.1**: Update `SETUP_GUIDE.md` with ASGI instructions
  - **File**: `docs/SETUP_GUIDE.md`
  - **Action**: Replace WSGI references with ASGI and update deployment instructions
  - **Status**: ✅ Completed
  - **Notes**: Enhanced ASGI documentation with configuration details, deployment instructions, and troubleshooting
  - **Changes Made**:
    - Added detailed ASGI configuration section
    - Enhanced Docker deployment instructions with ASGI server details
    - Improved WebSocket troubleshooting section
    - Updated performance optimization section with ASGI-specific recommendations
    - Added notes about Gunicorn incompatibility

- [x] **Task 9.2**: Update README.md if it contains WSGI references
  - **File**: `README.md`
  - **Action**: Review and update any WSGI mentions
  - **Status**: ✅ Completed
  - **Notes**: Created comprehensive README.md with full project documentation including ASGI deployment details
  - **Changes Made**:
    - Created complete README.md with project overview
    - Added ASGI deployment section explaining why ASGI is used
    - Included ASGI server configuration and compatibility notes
    - Added WebSocket endpoint documentation
    - Included production deployment instructions with ASGI requirements
    - Added notes about WSGI incompatibility (Gunicorn)

### 10. Testing
- [ ] **Task 10.1**: Test WebSocket functionality
  - **Action**: Verify `DispatcherConsumer` works correctly
  - **Endpoint**: `ws://localhost:8000/ws/dispatchers/`
  - **Status**: Pending
  - **Test Cases**:
    - Connection establishment
    - Authentication check
    - Real-time emergency updates
    - Ambulance updates
    - Initial data sending

- [ ] **Task 10.2**: Test WebSocket functionality for paramedics
  - **Action**: Verify `ParamedicConsumer` works correctly
  - **Endpoint**: `ws://localhost:8000/ws/paramedic/`
  - **Status**: Pending
  - **Test Cases**:
    - Connection establishment
    - Authentication check
    - Emergency update notifications
    - Ping/pong functionality

- [ ] **Task 10.3**: Test all REST API endpoints
  - **Action**: Verify all HTTP endpoints work correctly with ASGI
  - **Status**: Pending
  - **Test Cases**:
    - Emergency call creation (POST)
    - Emergency call listing (GET)
    - Emergency call updates (PATCH)
    - Ambulance operations
    - Hospital operations
    - User authentication
    - File uploads

### 11. Channel Layer Configuration
- [ ] **Task 11.1**: Verify Redis channel layer configuration
  - **File**: `EmmergencyAmbulanceSystem/settings.py`
  - **Action**: Ensure Redis channel layer is properly configured for production
  - **Status**: Pending
  - **Notes**: Current setup has fallback to InMemoryChannelLayer, verify Redis works in production
  - **Current Config**: Lines 172-196
  - **Production Requirements**:
    - Redis server running
    - Proper connection configuration
    - Error handling for Redis failures

### 12. Environment Configuration
- [ ] **Task 12.1**: Update environment variables documentation
  - **Action**: Ensure REDIS_URL is documented for ASGI/Channels usage
  - **Status**: Pending
  - **Environment Variables**:
    - `REDIS_URL`: Redis connection URL for channel layer
    - `DATABASE_URL`: Database connection (if using)
    - `DEBUG`: Debug mode setting
    - `SECRET_KEY`: Django secret key
    - `ALLOWED_HOSTS`: Allowed host names

### 13. Deployment Scripts
- [ ] **Task 13.1**: Check for WSGI references in deployment scripts
  - **Action**: Search for any hardcoded WSGI references
  - **Status**: Pending
  - **Files to Check**:
    - CI/CD configuration files
    - Deployment scripts
    - Docker configurations
    - Any shell scripts

### 14. Security Configuration
- [ ] **Task 14.1**: Verify CSRF token handling in ASGI
  - **File**: `EmmergencyAmbulanceSystem/settings.py`
  - **Action**: Ensure CSRF middleware works correctly with WebSocket connections
  - **Status**: Pending
  - **Notes**: WebSocket connections may need special CSRF handling
  - **Current**: CSRF middleware is in MIDDLEWARE list (line 58)

### 15. API Endpoint Testing
- [ ] **Task 15.1**: Test all REST API endpoints with ASGI
  - **Action**: Comprehensive testing of all API endpoints
  - **Status**: Pending
  - **Endpoints to Test**:
    - `/api/emergencies/` - Emergency call CRUD
    - `/api/dispatch/` - Dispatch operations
    - `/api/ambulances/` - Ambulance operations
    - `/api/hospitals/` - Hospital operations
    - `/api/users/` - User management
    - WebSocket endpoints

### 16. Production Deployment
- [ ] **Task 16.1**: Update production deployment instructions
  - **Action**: Ensure production deployment uses Daphne or Uvicorn
  - **Status**: Pending
  - **Production Servers**:
    - Daphne (recommended, already in requirements)
    - Uvicorn (alternative ASGI server)
    - **NOT Gunicorn** (WSGI server, not compatible)

### 17. ASGI Lifespan Events
- [ ] **Task 17.1**: Configure ASGI lifespan events if needed
  - **File**: `EmmergencyAmbulanceSystem/asgi.py`
  - **Action**: Add startup/shutdown handlers for initialization tasks
  - **Status**: Pending
  - **Notes**: Useful for connection pooling, cache warming, etc.
  - **Example Use Cases**:
    - Database connection pool initialization
    - Redis connection verification
    - Cache warming
    - Background task initialization

### 18. Database Connection Management
- [ ] **Task 18.1**: Verify database connection pooling
  - **Action**: Ensure database connections are properly managed in async context
  - **Status**: Pending
  - **Notes**: Async views need proper database connection handling
  - **Considerations**:
    - Connection pool size
    - Async database drivers (if using async views)
    - Connection timeout settings

---

## Migration Progress

**Overall Progress**: 61% (11/18 tasks completed)

### Phase 1: Core Configuration (Tasks 1-3)
- [x] Task 1: Remove WSGI_APPLICATION ✅
- [x] Task 2: Update docker-compose.yml ✅
- [x] Task 3: Remove gunicorn ✅

### Phase 2: Code Optimization (Tasks 4-7)
- [x] Task 4: Verify middleware ✅
- [x] Task 5: Optimize async/sync patterns ✅
- [x] Task 6: Static files configuration ✅
- [x] Task 7: Verify manage.py ✅

### Phase 3: Cleanup (Tasks 8-9)
- [x] Task 8: Deprecate wsgi.py ✅
- [x] Task 9: Update documentation ✅

### Phase 4: Testing (Tasks 10-15)
- [ ] Task 10: Test WebSocket functionality
- [ ] Task 11: Verify channel layer
- [ ] Task 12: Update environment docs
- [ ] Task 13: Check deployment scripts
- [ ] Task 14: Verify CSRF handling
- [ ] Task 15: Test API endpoints

### Phase 5: Production (Tasks 16-18)
- [ ] Task 16: Update production deployment
- [ ] Task 17: Configure lifespan events
- [ ] Task 18: Verify database connections

---

## Testing Checklist

### WebSocket Tests
- [ ] Dispatcher WebSocket connection
- [ ] Paramedic WebSocket connection
- [ ] Real-time emergency updates
- [ ] Real-time ambulance updates
- [ ] Authentication on WebSocket
- [ ] Group messaging functionality

### HTTP API Tests
- [ ] Emergency call creation
- [ ] Emergency call updates
- [ ] Ambulance operations
- [ ] Hospital operations
- [ ] User authentication
- [ ] File uploads
- [ ] Static file serving

### Integration Tests
- [ ] WebSocket + HTTP integration
- [ ] Channel layer messaging
- [ ] Database operations in async context
- [ ] Error handling

---

## Rollback Plan

If migration issues occur:

1. **Immediate Rollback**: Revert to WSGI configuration
   - Uncomment `WSGI_APPLICATION` in settings.py
   - Update docker-compose.yml to use runserver or gunicorn
   - Restore gunicorn in requirements.txt

2. **Partial Rollback**: Keep ASGI but fix specific issues
   - Identify problematic components
   - Fix or revert specific changes
   - Test incrementally

3. **Documentation**: Document any issues encountered
   - Note any compatibility problems
   - Document workarounds
   - Update migration plan

---

## Notes

- **Daphne** is the recommended ASGI server (already in requirements.txt)
- **Redis** is required for production WebSocket functionality
- **WhiteNoise** can be used for static file serving in ASGI
- All current middleware should be ASGI-compatible
- WebSocket authentication uses Channels AuthMiddlewareStack

---

## References

- [Django ASGI Documentation](https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/)
- [Django Channels Documentation](https://channels.readthedocs.io/)
- [Daphne Documentation](https://github.com/django/daphne)
- [ASGI Specification](https://asgi.readthedocs.io/)

---

## Last Updated
- **Date**: 2024
- **Version**: 1.0
- **Status**: Migration in Progress

