# Server Logging and Debugging Guide

## Issue: Server Console Shows No Output

When running Daphne, the terminal may appear blank or show no output. This guide helps you see what's happening.

## Why No Output?

Daphne may not show logs by default, or logging might be configured to only show warnings/errors. We've updated the logging configuration to show more information.

## Solutions

### Solution 1: Restart Server with Verbose Logging

The logging configuration has been updated to show:
- WebSocket connection attempts
- Authentication status
- Channel layer activity
- Server startup messages

**Restart the server:**
1. Stop the current server (Ctrl+C in the terminal where it's running)
2. Restart with:
   ```bash
   daphne -b 0.0.0.0 -p 8000 EmmergencyAmbulanceSystem.asgi:application
   ```

### Solution 2: Run with Explicit Verbose Flag

Some Daphne versions support verbose output:
```bash
daphne -v 2 -b 0.0.0.0 -p 8000 EmmergencyAmbulanceSystem.asgi:application
```

### Solution 3: Check Server Status

**Verify server is running:**
```bash
# Check if port 8000 is listening
netstat -ano | findstr :8000

# Check Python processes
tasklist | findstr python
```

**Test if server responds:**
```bash
curl http://localhost:8000/
```

### Solution 4: Check Logs in Different Ways

**Option A: Run in Foreground (Not Background)**
- Don't run with `&` or in background
- Keep terminal visible to see output

**Option B: Redirect Output to File**
```bash
daphne -b 0.0.0.0 -p 8000 EmmergencyAmbulanceSystem.asgi:application > server.log 2>&1
```
Then monitor the log file:
```bash
tail -f server.log
```

**Option C: Use Python's Logging**
The updated settings.py now includes logging configuration that should output to console.

## What You Should See

When the server starts correctly, you should see:

```
INFO Starting server at tcp:port=8000:interface=0.0.0.0
INFO HTTP/2 support not enabled (install the http2 and tls Twisted extras)
INFO Configuring endpoint tcp:port=8000:interface=0.0.0.0
INFO Listening on TCP address 0.0.0.0:8000
```

When a WebSocket connection is attempted, you should see:

```
INFO WebSocket connection attempt - User: <username>, Is Authenticated: True/False, Is Dispatcher: True/False
```

If connection is rejected:
```
WARNING WebSocket connection rejected - User: <user>, Is Authenticated: True/False, Is Dispatcher: True/False
```

## Troubleshooting Silent Server

### Check 1: Is Server Actually Running?
```bash
netstat -ano | findstr :8000
```
If you see `LISTENING` on port 8000, server is running.

### Check 2: Can You Access the Website?
Open browser: `http://localhost:8000/`
- If page loads: Server is working, just not showing logs
- If connection refused: Server is not running

### Check 3: Check for Errors
Even if no output, check:
- Windows Event Viewer
- Check if process is consuming CPU (might be stuck in a loop)
- Check if port is actually listening

### Check 4: Test WebSocket Connection
Open browser console and try:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/dispatchers/');
ws.onopen = () => console.log('Connected!');
ws.onerror = (e) => console.error('Error:', e);
ws.onclose = (e) => console.log('Closed:', e.code, e.reason);
```

## Expected Behavior

**Normal Operation:**
- Server starts and listens on port 8000
- No output until a request comes in
- When WebSocket connects, you see log messages
- When HTTP request comes in, you might see Django logs

**If You See Nothing:**
- Server might be running but not logging
- Check if you can access `http://localhost:8000/` in browser
- Try making a request to trigger logs
- Check browser console for WebSocket errors

## Next Steps

1. **Restart server** with updated logging configuration
2. **Open browser** to `http://localhost:8000/dashboard/` (while logged in as dispatcher)
3. **Watch terminal** for WebSocket connection logs
4. **Check browser console** for WebSocket connection status

If still no output, the server might be working but just not verbose. The important thing is whether WebSocket connections work, not whether you see logs.

