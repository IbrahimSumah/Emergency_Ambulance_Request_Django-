# WebSocket Connection Debugging Guide

This guide helps diagnose and fix WebSocket connection issues ("WS: CLOSED" errors).

## 🔍 Common Issues and Solutions

### Issue 1: WebSocket Connection Immediately Closes

**Symptoms:**
- Connection establishes then immediately closes
- Status shows "WS: CLOSED"
- Error message: "Realtime disabled, switching to periodic updates"

**Possible Causes:**

#### 1.1: Authentication Failure
**Problem**: User is not authenticated or doesn't have the correct role.

**Diagnosis:**
- Check server logs for: `"WebSocket connection rejected"`
- Look for authentication warnings in logs

**Solution:**
1. Ensure you're logged in as the correct user:
   - **Dispatcher**: Must have `role='dispatcher'`
   - **Paramedic**: Must have `role='paramedic'`

2. Verify user authentication:
   ```python
   python manage.py shell
   ```
   ```python
   from core.models import User
   user = User.objects.get(username='test_dispatcher')
   print(f"Role: {user.role}")
   print(f"Is Dispatcher: {user.is_dispatcher}")
   print(f"Is Authenticated: {user.is_authenticated}")
   ```

3. Check browser cookies:
   - Open browser DevTools (F12)
   - Go to Application/Storage → Cookies
   - Verify `sessionid` cookie exists
   - Cookie should be set when you login

#### 1.2: Server Not Running with ASGI
**Problem**: Server is running with development server (`runserver`) instead of Daphne.

**Diagnosis:**
- Check server startup command
- Development server has limited WebSocket support

**Solution:**
```bash
# Stop current server
# Start with Daphne ASGI server
daphne -b 0.0.0.0 -p 8000 EmmergencyAmbulanceSystem.asgi:application
```

#### 1.3: Session Cookie Not Being Sent
**Problem**: WebSocket connections don't automatically send cookies in all browsers/environments.

**Diagnosis:**
- Check browser console for connection errors
- Verify cookies are being sent in WebSocket handshake

**Solution:**
1. Ensure same-origin policy: WebSocket URL must match HTTP origin
2. Check if cookies are enabled in browser
3. Try clearing cookies and logging in again

#### 1.4: CORS Issues
**Problem**: Cross-origin requests blocking WebSocket connection.

**Diagnosis:**
- Check browser console for CORS errors
- Verify WebSocket URL matches page origin

**Solution:**
- Ensure WebSocket connects to same origin as page
- If using different port/domain, add to `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS`

---

### Issue 2: WebSocket Connection Fails to Establish

**Symptoms:**
- Connection never opens
- Status shows "WS: CLOSED" immediately
- No connection attempt logged

**Possible Causes:**

#### 2.1: Server Not Running
**Problem**: ASGI server is not running.

**Solution:**
```bash
# Start server
daphne -b 0.0.0.0 -p 8000 EmmergencyAmbulanceSystem.asgi:application
```

#### 2.2: Port Mismatch
**Problem**: WebSocket URL points to wrong port.

**Solution:**
- Verify server is running on port 8000
- Check WebSocket URL in browser console
- Ensure `location.host` matches server port

#### 2.3: Firewall/Network Issues
**Problem**: Firewall blocking WebSocket connections.

**Solution:**
- Check firewall settings
- Ensure port 8000 is open
- Try connecting from same machine

---

### Issue 3: WebSocket Connects But No Messages Received

**Symptoms:**
- Connection shows "WS: CONNECTED"
- No initial data received
- No real-time updates

**Possible Causes:**

#### 3.1: Channel Layer Not Working
**Problem**: Redis not running or InMemory channel layer not working.

**Diagnosis:**
```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG
```

**Solution:**
1. **Option A**: Start Redis
   ```bash
   redis-server
   ```

2. **Option B**: Use InMemory channel layer (current fallback)
   - Should work for development
   - Not suitable for production with multiple server instances

#### 3.2: Consumer Not Sending Initial Data
**Problem**: Error in consumer code preventing initial data send.

**Diagnosis:**
- Check server logs for errors
- Look for database query errors
- Check serializer errors

**Solution:**
- Review server logs when connecting
- Fix any database/serializer errors
- Ensure test data exists (ambulances, hospitals)

---

## 🔧 Step-by-Step Debugging Process

### Step 1: Check Server Logs

When you try to connect, watch the server console for:

```
INFO WebSocket connection attempt - User: <user>, Is Authenticated: True/False, Is Dispatcher: True/False
```

**If you see "Is Authenticated: False":**
- User is not logged in
- Session cookie not being sent
- Solution: Login again, ensure cookies enabled

**If you see "Is Dispatcher: False":**
- User doesn't have dispatcher role
- Solution: Verify user role in database

**If you see connection rejected warning:**
- Authentication or authorization failed
- Check user role and authentication status

### Step 2: Check Browser Console

Open browser DevTools (F12) → Console tab:

```javascript
// Check WebSocket connection
const ws = new WebSocket('ws://localhost:8000/ws/dispatchers/');
ws.onopen = () => console.log('Connected!');
ws.onmessage = (e) => console.log('Message:', e.data);
ws.onerror = (e) => console.error('Error:', e);
ws.onclose = (e) => console.log('Closed:', e.code, e.reason);
```

**Look for:**
- Connection errors
- Close codes (4001 = unauthorized)
- Network errors

### Step 3: Verify Authentication

**Check if user is authenticated:**
1. Login to the application
2. Open browser console
3. Check session cookie exists
4. Try accessing `/api/emergencies/` - should work if authenticated

**Check user role:**
```python
python manage.py shell
```
```python
from core.models import User
user = User.objects.get(username='your_username')
print(f"Role: {user.role}")
print(f"Is Dispatcher: {user.is_dispatcher}")
print(f"Is Paramedic: {user.is_paramedic}")
```

### Step 4: Test WebSocket with Testing Tool

1. Login as dispatcher: `http://localhost:8000/login/`
2. Open testing tool: `http://localhost:8000/test/websocket/`
3. Select "Dispatcher" from dropdown
4. Click "Connect"
5. Check logs for connection attempt
6. Review error messages

### Step 5: Check Channel Layer

**If using Redis:**
```bash
redis-cli ping
# Should return: PONG

# Check Redis is accepting connections
redis-cli info
```

**If using InMemory:**
- Should work automatically
- No additional setup needed
- Check server logs for channel layer errors

---

## 🐛 Quick Fixes

### Fix 1: Re-login
```bash
# Clear browser cookies
# Login again at http://localhost:8000/login/
```

### Fix 2: Restart Server with Daphne
```bash
# Stop current server (Ctrl+C)
daphne -b 0.0.0.0 -p 8000 EmmergencyAmbulanceSystem.asgi:application
```

### Fix 3: Verify User Role
```python
python manage.py shell
```
```python
from core.models import User
user = User.objects.get(username='test_dispatcher')
if user.role != 'dispatcher':
    user.role = 'dispatcher'
    user.save()
    print("Fixed user role")
```

### Fix 4: Check ALLOWED_HOSTS
Ensure `ALLOWED_HOSTS` includes your domain:
```python
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']
```

### Fix 5: Clear Browser Cache
- Clear browser cache
- Clear cookies for localhost
- Restart browser
- Try again

---

## 📊 Diagnostic Checklist

Use this checklist to systematically diagnose the issue:

- [ ] Server is running with Daphne (not `runserver`)
- [ ] User is logged in (check cookies)
- [ ] User has correct role (dispatcher/paramedic)
- [ ] ALLOWED_HOSTS includes localhost/127.0.0.1
- [ ] WebSocket URL matches page origin
- [ ] Browser cookies are enabled
- [ ] No CORS errors in browser console
- [ ] Channel layer is working (Redis or InMemory)
- [ ] Server logs show connection attempts
- [ ] No errors in server logs
- [ ] Database migrations applied
- [ ] Test data exists (for initial data)

---

## 🔍 Advanced Debugging

### Enable Verbose Logging

Edit `settings.py` to enable verbose logging:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'emergencies.consumers': {
            'handlers': ['console'],
            'level': 'DEBUG',  # Changed from INFO to DEBUG
        },
        'channels': {
            'handlers': ['console'],
            'level': 'DEBUG',  # Changed from WARNING to DEBUG
        },
        'channels.auth': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### Check WebSocket Handshake

Use browser DevTools → Network tab:
1. Filter by "WS" (WebSocket)
2. Look for `/ws/dispatchers/` or `/ws/paramedic/`
3. Check request headers for cookies
4. Check response status code

### Test Authentication Manually

```python
python manage.py shell
```
```python
from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model
User = get_user_model()

# List active sessions
for session in Session.objects.all():
    data = session.get_decoded()
    if '_auth_user_id' in data:
        user = User.objects.get(id=data['_auth_user_id'])
        print(f"Session: {session.session_key}, User: {user.username}, Role: {user.role}")
```

---

## 📝 Common Error Codes

- **4000-3999**: Normal closure
- **4001**: Unauthorized (user not authenticated or wrong role) ← **Most common**
- **4002**: Invalid request
- **4003**: Server error
- **1000**: Normal closure (clean disconnect)

---

## ✅ Success Indicators

When WebSocket is working correctly, you should see:

1. **Server logs:**
   ```
   INFO WebSocket connection attempt - User: test_dispatcher, Is Authenticated: True, Is Dispatcher: True
   ```

2. **Browser console:**
   - Connection opens
   - Initial data received
   - Ping/pong works

3. **Dashboard:**
   - "WS: CONNECTED" status (green)
   - Real-time updates working
   - No "switching to periodic updates" message

---

## 🆘 Still Having Issues?

If none of the above solutions work:

1. **Check server logs** for specific error messages
2. **Share error logs** from server console
3. **Check browser console** for client-side errors
4. **Verify Django Channels version** is compatible
5. **Check for conflicting middleware** or settings
6. **Test with minimal setup** (new browser session, fresh login)

---

## 📚 Additional Resources

- Django Channels Documentation: https://channels.readthedocs.io/
- WebSocket API: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket
- ASGI Specification: https://asgi.readthedocs.io/

