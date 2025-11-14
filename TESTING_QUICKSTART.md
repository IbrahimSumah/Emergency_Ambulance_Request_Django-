# Testing Quick Start Guide

This guide will help you test the ASGI WebSocket and API functionality step by step.

## 📋 Prerequisites

Before starting, ensure:

1. **Server is running with ASGI**:
   ```bash
   daphne -b 0.0.0.0 -p 8000 EmmergencyAmbulanceSystem.asgi:application
   ```

2. **Test users exist** (create if needed):
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
   
   # Create ambulance (optional, for full testing)
   from dispatch.models import Ambulance, Hospital
   ambulance = Ambulance.objects.create(
       unit_number='TEST-001',
       status='AVAILABLE',
       base_station='Test Station',
       assigned_paramedic=paramedic
   )
   
   hospital = Hospital.objects.create(
       name='Test Hospital',
       address='123 Test St',
       latitude=40.7128,
       longitude=-74.0060,
       phone='555-0123',
       total_beds=100,
       available_beds=50
   )
   ```

3. **Install testing dependencies** (optional):
   ```bash
   pip install websockets
   ```

---

## 🚀 Step-by-Step Testing

### Step 1: Test REST API Endpoints (Automated)

Run the automated test script:

```bash
python test_asgi_functionality.py
```

This will test:
- Emergency call creation
- Emergency call listing
- Emergency call retrieval
- Emergency call update
- Emergency status update
- Active emergencies
- Ambulance listing
- Hospital listing

**Expected Output**: All API tests should pass (green checkmarks).

---

### Step 2: Test Dispatcher WebSocket (Manual)

#### Option A: Using the Web Testing Tool (Recommended)

1. **Start the server** (if not already running):
   ```bash
   daphne -b 0.0.0.0 -p 8000 EmmergencyAmbulanceSystem.asgi:application
   ```

2. **Login as dispatcher**:
   - Open browser: `http://localhost:8000/login/`
   - Login with: `test_dispatcher` / `testpass123`

3. **Open WebSocket testing tool**:
   - Navigate to: `http://localhost:8000/test/websocket/`
   - Select "Dispatcher" from dropdown
   - Click "Connect"
   - You should see: "Status: Connected" (green)
   - You should receive an "initial_data" message with emergencies, ambulances, and hospitals

4. **Test ping/pong**:
   - Click "Send Ping"
   - You should receive: `{"type": "pong"}`

5. **Test initial data request**:
   - Click "Request Initial Data"
   - You should receive: `{"type": "initial_data", "data": {...}}`

6. **Test real-time updates**:
   - Open another terminal/window
   - Create a new emergency call:
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
   - You should see a `emergency_update` message in the WebSocket testing tool

#### Option B: Using Browser Console (Alternative)

1. **Login as dispatcher** in browser
2. **Open browser console** (F12)
3. **Run this code**:
   ```javascript
   const ws = new WebSocket('ws://localhost:8000/ws/dispatchers/');
   ws.onopen = () => console.log('Connected!');
   ws.onmessage = (event) => console.log('Message:', JSON.parse(event.data));
   ws.onerror = (error) => console.error('Error:', error);
   ws.send(JSON.stringify({type: 'ping'}));
   ```

**Expected Result**: 
- Connection established
- Initial data received
- Ping/pong works
- Real-time updates received

---

### Step 3: Test Paramedic WebSocket (Manual)

1. **Login as paramedic**:
   - Open browser: `http://localhost:8000/login/`
   - Login with: `test_paramedic` / `testpass123`

2. **Open WebSocket testing tool**:
   - Navigate to: `http://localhost:8000/test/websocket/`
   - Select "Paramedic" from dropdown
   - Click "Connect"
   - You should see: "Status: Connected" (green)

3. **Test ping/pong**:
   - Click "Send Ping"
   - You should receive: `{"type": "pong"}`

4. **Test emergency notifications**:
   - In another terminal, assign an emergency to this paramedic:
     ```bash
     curl -X PATCH http://localhost:8000/api/emergencies/1/ \
       -H "Content-Type: application/json" \
       -d '{
         "assigned_paramedic": 2,
         "assigned_ambulance": 1
       }'
     ```
   - Update emergency status:
     ```bash
     curl -X PATCH http://localhost:8000/api/emergencies/1/status/ \
       -H "Content-Type: application/json" \
       -d '{"status": "EN_ROUTE"}'
     ```
   - You should see `emergency_update` messages in the WebSocket testing tool

**Expected Result**:
- Connection established
- Ping/pong works
- Emergency notifications received

---

### Step 4: Test Authentication Rejection

#### Test Unauthenticated Connection:
1. **Open WebSocket testing tool** (without logging in)
2. **Try to connect** to dispatcher WebSocket
3. **Expected**: Connection should close immediately (code 1000 or 4000+)

#### Test Wrong Role:
1. **Login as paramedic**
2. **Try to connect** to dispatcher WebSocket
3. **Expected**: Connection should close immediately

**Expected Result**: Unauthorized users are rejected

---

### Step 5: Test All REST API Endpoints (Manual)

Use the detailed testing guide: `docs/TESTING_GUIDE.md`

Or test manually using curl:

```bash
# Emergency calls
curl -X GET http://localhost:8000/api/emergencies/
curl -X POST http://localhost:8000/api/emergencies/ -H "Content-Type: application/json" -d '{...}'
curl -X GET http://localhost:8000/api/emergencies/1/
curl -X PATCH http://localhost:8000/api/emergencies/1/ -H "Content-Type: application/json" -d '{...}'

# Ambulances
curl -X GET http://localhost:8000/api/ambulances/
curl -X POST http://localhost:8000/api/ambulances/ -H "Content-Type: application/json" -d '{...}'

# Hospitals
curl -X GET http://localhost:8000/api/hospitals/
curl -X POST http://localhost:8000/api/hospitals/ -H "Content-Type: application/json" -d '{...}'
```

---

## ✅ Testing Checklist

Use this checklist to track your progress:

### WebSocket Tests
- [ ] **Task 10.1.1**: Dispatcher connection establishment
- [ ] **Task 10.1.2**: Dispatcher authentication check (rejects non-dispatchers)
- [ ] **Task 10.1.3**: Dispatcher initial data sending
- [ ] **Task 10.1.4**: Dispatcher real-time emergency updates
- [ ] **Task 10.1.5**: Dispatcher real-time ambulance updates
- [ ] **Task 10.1.6**: Dispatcher ping/pong
- [ ] **Task 10.1.7**: Dispatcher request initial data
- [ ] **Task 10.2.1**: Paramedic connection establishment
- [ ] **Task 10.2.2**: Paramedic authentication check (rejects non-paramedics)
- [ ] **Task 10.2.3**: Paramedic emergency update notifications
- [ ] **Task 10.2.4**: Paramedic ping/pong

### REST API Tests
- [ ] **Task 10.3.1**: Emergency call creation
- [ ] **Task 10.3.2**: Emergency call listing
- [ ] **Task 10.3.3**: Emergency call retrieval
- [ ] **Task 10.3.4**: Emergency call update
- [ ] **Task 10.3.5**: Emergency status update
- [ ] **Task 10.3.6**: Active emergencies
- [ ] **Task 10.3.7**: File upload
- [ ] **Task 10.3.8**: Ambulance list
- [ ] **Task 10.3.9**: Ambulance creation
- [ ] **Task 10.3.10**: Ambulance update
- [ ] **Task 10.3.11**: Ambulance location update
- [ ] **Task 10.3.12**: Dispatch ambulance
- [ ] **Task 10.3.13**: Hospital list
- [ ] **Task 10.3.14**: Hospital creation
- [ ] **Task 10.3.15**: Hospital capacity update
- [ ] **Task 10.3.16**: User authentication
- [ ] **Task 10.3.17**: User list

---

## 🐛 Troubleshooting

### WebSocket Connection Fails
- **Issue**: Connection refused or closes immediately
- **Solutions**:
  - Ensure using ASGI server (Daphne), not development server
  - Make sure you're logged in as the correct user (dispatcher/paramedic)
  - Check browser console for errors
  - Verify server is running on correct port

### API Requests Fail
- **Issue**: 500 Internal Server Error
- **Solutions**:
  - Check server logs for errors
  - Verify database migrations are applied: `python manage.py migrate`
  - Check required fields in request body
  - Verify JSON format is correct

### No WebSocket Notifications
- **Issue**: API calls succeed but no WebSocket messages
- **Solutions**:
  - Verify WebSocket is connected
  - Check channel layer configuration (Redis or InMemory)
  - Verify notification functions are called in views
  - Check server logs for channel layer errors

---

## 📚 Additional Resources

- **Detailed Testing Guide**: `docs/TESTING_GUIDE.md`
- **Migration Document**: `MIGRATION_WSGI_TO_ASGI.md`
- **Setup Guide**: `docs/SETUP_GUIDE.md`

---

## 🎯 Next Steps

After completing all tests:

1. **Document any issues** found during testing
2. **Fix any bugs** discovered
3. **Update migration document** with test results
4. **Proceed to next migration tasks** (Task 11-18)

---

## 📝 Notes

- The automated test script (`test_asgi_functionality.py`) tests API endpoints only
- WebSocket tests require manual testing due to authentication requirements
- The WebSocket testing tool at `/test/websocket/` requires browser-based authentication
- For production testing, ensure Redis is running for channel layer


