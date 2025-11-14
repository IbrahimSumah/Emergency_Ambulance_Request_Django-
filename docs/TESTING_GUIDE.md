# ASGI WebSocket and API Testing Guide

This guide provides step-by-step instructions for testing WebSocket functionality and REST API endpoints after the WSGI to ASGI migration.

## Prerequisites

Before starting tests, ensure:

1. **Server is running with ASGI**:
   ```bash
   # Using Daphne (recommended)
   daphne -b 0.0.0.0 -p 8000 EmmergencyAmbulanceSystem.asgi:application
   
   # OR using development server (limited WebSocket support)
   python manage.py runserver
   ```

2. **Redis is running** (optional but recommended for production-like testing):
   ```bash
   redis-server
   ```

3. **Test users exist**:
   - Dispatcher user (role='dispatcher')
   - Paramedic user (role='paramedic')
   - Admin user (optional)

4. **Test data exists**:
   - At least one ambulance
   - At least one hospital
   - Sample emergency calls (optional, can be created during testing)

## Test Setup

### Create Test Users (if not already created)

```bash
python manage.py shell
```

```python
from core.models import User
from dispatch.models import Ambulance, Hospital

# Create dispatcher
dispatcher = User.objects.create_user(
    username='test_dispatcher',
    email='dispatcher@test.com',
    password='testpass123',
    first_name='Test',
    last_name='Dispatcher',
    role='dispatcher'
)

# Create paramedic
paramedic = User.objects.create_user(
    username='test_paramedic',
    email='paramedic@test.com',
    password='testpass123',
    first_name='Test',
    last_name='Paramedic',
    role='paramedic'
)

# Create ambulance
ambulance = Ambulance.objects.create(
    unit_number='TEST-001',
    status='AVAILABLE',
    base_station='Test Station',
    assigned_paramedic=paramedic
)

# Create hospital
hospital = Hospital.objects.create(
    name='Test Hospital',
    address='123 Test St',
    latitude=40.7128,
    longitude=-74.0060,
    phone='555-0123',
    total_beds=100,
    available_beds=50
)

print("Test data created successfully!")
```

---

## Task 10.1: Test Dispatcher WebSocket Functionality

### Endpoint
- **URL**: `ws://localhost:8000/ws/dispatchers/`
- **Consumer**: `DispatcherConsumer`
- **Authentication**: Required (must be dispatcher user)

### Test 10.1.1: Connection Establishment

**Objective**: Verify WebSocket connection can be established successfully.

**Steps**:
1. Open browser console or use WebSocket client tool
2. Authenticate as dispatcher user first (get session cookie or token)
3. Connect to WebSocket endpoint
4. Verify connection is accepted

**Expected Result**: 
- Connection established successfully
- WebSocket receives `initial_data` message immediately after connection
- Connection remains open

**Manual Test**:
```javascript
// In browser console (while logged in as dispatcher)
const ws = new WebSocket('ws://localhost:8000/ws/dispatchers/');
ws.onopen = () => console.log('Connected!');
ws.onmessage = (event) => console.log('Message:', JSON.parse(event.data));
ws.onerror = (error) => console.error('Error:', error);
```

### Test 10.1.2: Authentication Check

**Objective**: Verify unauthorized users are rejected.

**Steps**:
1. Try to connect without authentication
2. Try to connect as non-dispatcher user (e.g., paramedic)
3. Verify connection is closed immediately

**Expected Result**:
- Connection closes immediately if user is not authenticated
- Connection closes if user is not a dispatcher

### Test 10.1.3: Initial Data Sending

**Objective**: Verify initial data is sent upon connection.

**Steps**:
1. Connect as dispatcher
2. Wait for initial data message
3. Verify data structure contains emergencies, ambulances, and hospitals

**Expected Result**:
```json
{
  "type": "initial_data",
  "data": {
    "emergencies": [...],
    "ambulances": [...],
    "hospitals": [...]
  }
}
```

### Test 10.1.4: Real-time Emergency Updates

**Objective**: Verify dispatcher receives real-time emergency call updates.

**Steps**:
1. Connect dispatcher WebSocket
2. Create a new emergency call via API (in another terminal/window)
3. Verify dispatcher receives `emergency_update` message

**Expected Result**:
```json
{
  "type": "emergency_update",
  "event": "created",
  "data": { /* emergency call data */ }
}
```

**API Call to Trigger Update**:
```bash
curl -X POST http://localhost:8000/api/emergencies/ \
  -H "Content-Type: application/json" \
  -d '{
    "caller_name": "John Doe",
    "caller_phone": "0881234567",
    "emergency_type": "MEDICAL",
    "description": "Test emergency",
    "location_address": "123 Test St",
    "latitude": "40.7128",
    "longitude": "-74.0060",
    "priority": "HIGH"
  }'
```

### Test 10.1.5: Real-time Ambulance Updates

**Objective**: Verify dispatcher receives real-time ambulance status updates.

**Steps**:
1. Connect dispatcher WebSocket
2. Update ambulance location or status via API
3. Verify dispatcher receives `ambulance_update` message

**Expected Result**:
```json
{
  "type": "ambulance_update",
  "event": "location_updated",
  "data": { /* ambulance data */ }
}
```

**API Call to Trigger Update**:
```bash
curl -X POST http://localhost:8000/api/ambulances/1/location/ \
  -H "Content-Type: application/json" \
  -d '{
    "current_latitude": "40.7580",
    "current_longitude": "-73.9855"
  }'
```

### Test 10.1.6: Ping/Pong Functionality

**Objective**: Verify ping/pong keepalive works.

**Steps**:
1. Connect dispatcher WebSocket
2. Send ping message: `{"type": "ping"}`
3. Verify pong response: `{"type": "pong"}`

**Expected Result**:
- Ping message accepted
- Pong response received immediately

### Test 10.1.7: Request Initial Data

**Objective**: Verify initial data can be requested on demand.

**Steps**:
1. Connect dispatcher WebSocket
2. Send: `{"type": "get_initial_data"}`
3. Verify initial data is sent again

**Expected Result**:
- Initial data message received with all current data

---

## Task 10.2: Test Paramedic WebSocket Functionality

### Endpoint
- **URL**: `ws://localhost:8000/ws/paramedic/`
- **Consumer**: `ParamedicConsumer`
- **Authentication**: Required (must be paramedic user)

### Test 10.2.1: Connection Establishment

**Objective**: Verify paramedic can connect to WebSocket.

**Steps**:
1. Authenticate as paramedic user
2. Connect to WebSocket endpoint
3. Verify connection is accepted

**Expected Result**: Connection established successfully

**Manual Test**:
```javascript
// In browser console (while logged in as paramedic)
const ws = new WebSocket('ws://localhost:8000/ws/paramedic/');
ws.onopen = () => console.log('Connected!');
ws.onmessage = (event) => console.log('Message:', JSON.parse(event.data));
ws.onerror = (error) => console.error('Error:', error);
```

### Test 10.2.2: Authentication Check

**Objective**: Verify unauthorized users are rejected.

**Steps**:
1. Try to connect without authentication
2. Try to connect as non-paramedic user
3. Verify connection is closed

**Expected Result**:
- Connection closes if user is not authenticated
- Connection closes if user is not a paramedic

### Test 10.2.3: Emergency Update Notifications

**Objective**: Verify paramedic receives notifications for assigned emergencies.

**Steps**:
1. Connect paramedic WebSocket
2. Assign an emergency to this paramedic via API
3. Update emergency status
4. Verify paramedic receives `emergency_update` message

**Expected Result**:
```json
{
  "type": "emergency_update",
  "event": "status_updated",
  "data": { /* emergency call data */ }
}
```

**API Calls to Trigger Updates**:
```bash
# Assign emergency to paramedic
curl -X PATCH http://localhost:8000/api/emergencies/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "assigned_paramedic": 2,
    "assigned_ambulance": 1
  }'

# Update emergency status
curl -X PATCH http://localhost:8000/api/emergencies/1/status/ \
  -H "Content-Type: application/json" \
  -d '{
    "status": "EN_ROUTE"
  }'
```

### Test 10.2.4: Ping/Pong Functionality

**Objective**: Verify ping/pong works for paramedics.

**Steps**:
1. Connect paramedic WebSocket
2. Send ping: `{"type": "ping"}`
3. Verify pong response

**Expected Result**: Pong received immediately

---

## Task 10.3: Test REST API Endpoints

All API endpoints should work correctly with ASGI server.

### Test 10.3.1: Emergency Call Creation (POST)

**Endpoint**: `POST /api/emergencies/`

**Objective**: Verify emergency calls can be created.

**Test**:
```bash
curl -X POST http://localhost:8000/api/emergencies/ \
  -H "Content-Type: application/json" \
  -d '{
    "caller_name": "John Doe",
    "caller_phone": "0881234567",
    "emergency_type": "MEDICAL",
    "description": "Patient needs immediate medical attention",
    "location_address": "123 Main St, City",
    "latitude": "40.7128",
    "longitude": "-74.0060",
    "priority": "HIGH"
  }'
```

**Expected Result**:
- Status: 201 Created
- Returns emergency call data with generated call_id
- WebSocket notification sent to dispatchers

### Test 10.3.2: Emergency Call Listing (GET)

**Endpoint**: `GET /api/emergencies/`

**Test**:
```bash
curl -X GET http://localhost:8000/api/emergencies/
```

**Expected Result**:
- Status: 200 OK
- Returns list of emergency calls

### Test 10.3.3: Emergency Call Retrieval (GET)

**Endpoint**: `GET /api/emergencies/{id}/`

**Test**:
```bash
curl -X GET http://localhost:8000/api/emergencies/1/
```

**Expected Result**:
- Status: 200 OK
- Returns specific emergency call data

### Test 10.3.4: Emergency Call Update (PATCH)

**Endpoint**: `PATCH /api/emergencies/{id}/`

**Test**:
```bash
curl -X PATCH http://localhost:8000/api/emergencies/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "status": "DISPATCHED",
    "assigned_ambulance": 1,
    "assigned_paramedic": 2
  }'
```

**Expected Result**:
- Status: 200 OK
- Returns updated emergency call data
- WebSocket notifications sent to relevant users

### Test 10.3.5: Emergency Status Update (PATCH)

**Endpoint**: `PATCH /api/emergencies/{id}/status/`

**Test**:
```bash
curl -X PATCH http://localhost:8000/api/emergencies/1/status/ \
  -H "Content-Type: application/json" \
  -d '{
    "status": "EN_ROUTE"
  }'
```

**Expected Result**:
- Status: 200 OK
- Emergency status updated
- Timestamps updated (e.g., en_route_at)
- WebSocket notifications sent

### Test 10.3.6: Active Emergencies (GET)

**Endpoint**: `GET /api/emergencies/active/`

**Test**:
```bash
curl -X GET "http://localhost:8000/api/emergencies/active/?status=active"
```

**Expected Result**:
- Status: 200 OK
- Returns filtered list of active emergencies

### Test 10.3.7: File Upload (POST)

**Endpoint**: `POST /api/emergencies/upload-image/`

**Test**:
```bash
curl -X POST http://localhost:8000/api/emergencies/upload-image/ \
  -F "image=@/path/to/test-image.jpg" \
  -F "call_id=1"
```

**Expected Result**:
- Status: 200 OK
- Image uploaded and saved
- Returns image URL and metadata
- Image added to emergency call's emergency_images field

### Test 10.3.8: Ambulance List (GET)

**Endpoint**: `GET /api/ambulances/`

**Test**:
```bash
curl -X GET http://localhost:8000/api/ambulances/
```

**Expected Result**:
- Status: 200 OK
- Returns list of ambulances

### Test 10.3.9: Ambulance Creation (POST)

**Endpoint**: `POST /api/ambulances/`

**Test**:
```bash
curl -X POST http://localhost:8000/api/ambulances/ \
  -H "Content-Type: application/json" \
  -d '{
    "unit_number": "AMB-002",
    "status": "AVAILABLE",
    "base_station": "Station 2"
  }'
```

**Expected Result**:
- Status: 201 Created
- Returns created ambulance data

### Test 10.3.10: Ambulance Update (PATCH)

**Endpoint**: `PATCH /api/ambulances/{id}/`

**Test**:
```bash
curl -X PATCH http://localhost:8000/api/ambulances/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "status": "DISPATCHED"
  }'
```

**Expected Result**:
- Status: 200 OK
- Returns updated ambulance data
- WebSocket notifications sent to dispatchers

### Test 10.3.11: Ambulance Location Update (POST)

**Endpoint**: `POST /api/ambulances/{id}/location/`

**Test**:
```bash
curl -X POST http://localhost:8000/api/ambulances/1/location/ \
  -H "Content-Type: application/json" \
  -d '{
    "current_latitude": "40.7580",
    "current_longitude": "-73.9855"
  }'
```

**Expected Result**:
- Status: 200 OK
- Ambulance location updated
- WebSocket notifications sent to dispatchers

### Test 10.3.12: Dispatch Ambulance (POST)

**Endpoint**: `POST /api/dispatch/`

**Test**:
```bash
curl -X POST http://localhost:8000/api/dispatch/ \
  -H "Content-Type: application/json" \
  -d '{
    "emergency_id": 1,
    "ambulance_id": 1,
    "paramedic_id": 2
  }'
```

**Expected Result**:
- Status: 200 OK
- Emergency call status updated to DISPATCHED
- Ambulance status updated
- WebSocket notifications sent

### Test 10.3.13: Hospital List (GET)

**Endpoint**: `GET /api/hospitals/`

**Test**:
```bash
curl -X GET http://localhost:8000/api/hospitals/
```

**Expected Result**:
- Status: 200 OK
- Returns list of hospitals

### Test 10.3.14: Hospital Creation (POST)

**Endpoint**: `POST /api/hospitals/`

**Test**:
```bash
curl -X POST http://localhost:8000/api/hospitals/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "City Hospital",
    "address": "456 Health Ave",
    "latitude": "40.7614",
    "longitude": "-73.9776",
    "phone": "555-0199",
    "total_beds": 200,
    "available_beds": 150
  }'
```

**Expected Result**:
- Status: 201 Created
- Returns created hospital data

### Test 10.3.15: Hospital Capacity Update (POST)

**Endpoint**: `POST /api/hospitals/{id}/capacity/`

**Test**:
```bash
curl -X POST http://localhost:8000/api/hospitals/1/capacity/ \
  -H "Content-Type: application/json" \
  -d '{
    "available_beds": 45
  }'
```

**Expected Result**:
- Status: 200 OK
- Hospital capacity updated
- WebSocket notifications sent to dispatchers

### Test 10.3.16: User Authentication

**Endpoints**: Login/Logout

**Test Login**:
```bash
curl -X POST http://localhost:8000/login/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test_dispatcher&password=testpass123" \
  -c cookies.txt
```

**Expected Result**:
- Status: 200 OK or 302 Redirect
- Session cookie set
- User authenticated

### Test 10.3.17: User List (GET) - Admin Only

**Endpoint**: `GET /api/users/`

**Test**:
```bash
curl -X GET http://localhost:8000/api/users/ \
  -b cookies.txt
```

**Expected Result**:
- Status: 200 OK (if admin)
- Status: 403 Forbidden (if not admin)
- Returns list of users

---

## Automated Testing Script

See `test_asgi_functionality.py` for automated testing script that can run all these tests programmatically.

## Testing Checklist

Use this checklist to track testing progress:

### WebSocket Tests
- [ ] Task 10.1.1: Dispatcher connection establishment
- [ ] Task 10.1.2: Dispatcher authentication check
- [ ] Task 10.1.3: Dispatcher initial data sending
- [ ] Task 10.1.4: Dispatcher real-time emergency updates
- [ ] Task 10.1.5: Dispatcher real-time ambulance updates
- [ ] Task 10.1.6: Dispatcher ping/pong
- [ ] Task 10.1.7: Dispatcher request initial data
- [ ] Task 10.2.1: Paramedic connection establishment
- [ ] Task 10.2.2: Paramedic authentication check
- [ ] Task 10.2.3: Paramedic emergency update notifications
- [ ] Task 10.2.4: Paramedic ping/pong

### REST API Tests
- [ ] Task 10.3.1: Emergency call creation
- [ ] Task 10.3.2: Emergency call listing
- [ ] Task 10.3.3: Emergency call retrieval
- [ ] Task 10.3.4: Emergency call update
- [ ] Task 10.3.5: Emergency status update
- [ ] Task 10.3.6: Active emergencies
- [ ] Task 10.3.7: File upload
- [ ] Task 10.3.8: Ambulance list
- [ ] Task 10.3.9: Ambulance creation
- [ ] Task 10.3.10: Ambulance update
- [ ] Task 10.3.11: Ambulance location update
- [ ] Task 10.3.12: Dispatch ambulance
- [ ] Task 10.3.13: Hospital list
- [ ] Task 10.3.14: Hospital creation
- [ ] Task 10.3.15: Hospital capacity update
- [ ] Task 10.3.16: User authentication
- [ ] Task 10.3.17: User list

---

## Troubleshooting

### WebSocket Connection Fails
- **Issue**: Connection refused or closed immediately
- **Solution**: 
  - Ensure using ASGI server (Daphne), not development server
  - Check authentication (must be logged in)
  - Verify user has correct role (dispatcher/paramedic)
  - Check Redis connection if using Redis channel layer

### API Requests Fail
- **Issue**: 500 Internal Server Error
- **Solution**:
  - Check server logs for errors
  - Verify database migrations are applied
  - Check required fields in request body
  - Verify authentication/authorization

### No WebSocket Notifications
- **Issue**: API calls succeed but no WebSocket messages
- **Solution**:
  - Verify WebSocket is connected
  - Check channel layer configuration
  - Verify notification functions are called in views
  - Check Redis connection if using Redis

---

## Next Steps

After completing all tests:
1. Document any issues found
2. Fix any bugs discovered
3. Update migration document with test results
4. Proceed to next migration tasks (Task 11-18)


