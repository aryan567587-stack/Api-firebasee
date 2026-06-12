# ✅ DEPLOYMENT CHECKLIST & TROUBLESHOOTING

## PRE-DEPLOYMENT CHECKLIST

### Files Present
- [ ] app.py (with keep-alive)
- [ ] config.py (bot token set)
- [ ] requirements.txt
- [ ] render.yaml (optimized)
- [ ] .env.example
- [ ] example_bot.py
- [ ] core/db.py
- [ ] core/extractor.py
- [ ] core/telegram.py
- [ ] templates/admin_login.html
- [ ] templates/admin_dashboard.html

### Configuration Check
- [ ] Bot token: 8725165662:AAFs_sfh50zGXW7Y6ZT1dNV488HN-q4Vieo
- [ ] Channel ID: -1003694677261
- [ ] Admin ID: 7949539794
- [ ] Admin password: Vishal12
- [ ] No confidential data in public files

---

## GITHUB UPLOAD CHECKLIST

### Step 1: Create Repository
- [ ] GitHub account active
- [ ] New repository created
- [ ] Name: aryan-api
- [ ] Visibility: Public
- [ ] No .gitignore needed

### Step 2: Upload Files
- [ ] All root files uploaded
- [ ] core/ folder created
- [ ] core/ has 3 Python files
- [ ] templates/ folder created
- [ ] templates/ has 2 HTML files
- [ ] Folder structure verified

### Step 3: Repository Status
- [ ] Can see all files on GitHub
- [ ] File count correct (11 files total)
- [ ] core/ folder visible
- [ ] templates/ folder visible
- [ ] Ready for deployment

---

## RENDER DEPLOYMENT CHECKLIST

### Step 1: Create Service
- [ ] Render account active
- [ ] New Web Service created
- [ ] GitHub connected
- [ ] aryan-api repository selected

### Step 2: Build Configuration
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `gunicorn -w 2 -b 0.0.0.0:$PORT --timeout 60 app:app`
- [ ] Region: Selected (Oregon recommended)
- [ ] Plan: Free or paid (Free works)

### Step 3: Environment Variables
- [ ] TG_BOT_TOKEN = 8725165662:AAFs_sfh50zGXW7Y6ZT1dNV488HN-q4Vieo
- [ ] TG_CHANNEL_ID = -1003694677261
- [ ] DEBUG = False
- [ ] All variables saved

### Step 4: Deploy
- [ ] Click "Deploy" button
- [ ] Wait 3-5 minutes
- [ ] Check deployment logs
- [ ] Service should be running

---

## POST-DEPLOYMENT VERIFICATION

### Health Checks
```
Test 1: Health Endpoint
URL: https://your-service.onrender.com/health
Expected: {"status": "healthy"}
Result: ✓ or ✗

Test 2: Home Endpoint
URL: https://your-service.onrender.com/
Expected: JSON with endpoints info
Result: ✓ or ✗

Test 3: Keep-Alive Ping
URL: https://your-service.onrender.com/ping
Expected: {"pong": true}
Result: ✓ or ✗
```

### Admin Panel
```
Test 4: Admin Login Page
URL: https://your-service.onrender.com/aryan
Expected: Login form appears
Result: ✓ or ✗

Test 5: Admin Login
ID: 7949539794
Password: Vishal12
Expected: Dashboard loads
Result: ✓ or ✗
```

### API Functionality
```
Test 6: Create API Key
Admin Panel → Create Key
Expected: New key generated
Result: ✓ or ✗

Test 7: Extract APK
Use API key to upload APK
Expected: Firebase config returned
Result: ✓ or ✗

Test 8: Telegram Message
Extract APK, check Telegram
Expected: Result in channel
Result: ✓ or ✗
```

### Keep-Alive Monitoring
```
Test 9: Check Keep-Alive
View Render logs for:
"Keep-alive ping sent ✓"
Expected: Every 10 minutes
Result: ✓ or ✗

Test 10: Service Status
Service should never sleep
Expected: Always responsive
Result: ✓ or ✗
```

---

## TROUBLESHOOTING GUIDE

### Issue: Service won't start
**Symptoms:** Build fails, service not starting
**Solutions:**
1. Check Render logs for errors
2. Verify all Python files present
3. Check requirements.txt syntax
4. Ensure AAPT installation in build

**Fix:**
```
1. Go to Render → Service → Logs
2. Look for error messages
3. Check that requirements.txt is valid
4. Redeploy if needed
```

---

### Issue: Admin login fails
**Symptoms:** Login page loads but login unsuccessful
**Solutions:**
1. Check ADMIN_ID: 7949539794
2. Check ADMIN_PASSWORD: Vishal12
3. Verify config.py deployed correctly
4. Check browser cookies enabled

**Fix:**
```
1. Verify credentials in config.py
2. Redeploy service
3. Clear browser cache
4. Try different browser
```

---

### Issue: APK extraction not working
**Symptoms:** /extract endpoint returns error
**Solutions:**
1. Verify API key is valid
2. Check quota is remaining
3. Ensure APK file is valid format
4. Check AAPT is installed

**Fix:**
```
1. Create new API key from admin panel
2. Check quota: /status endpoint
3. Use valid APK file
4. Check logs for AAPT errors
```

---

### Issue: Telegram not sending results
**Symptoms:** APK extracts but no Telegram message
**Solutions:**
1. Verify bot token: 8725165662:AAFs_sfh50zGXW7Y6ZT1dNV488HN-q4Vieo
2. Verify channel ID: -1003694677261
3. Check bot is admin in channel
4. Check Telegram integration in logs

**Fix:**
```
1. In config.py, verify bot token
2. Verify channel ID
3. Make sure bot is admin in channel
4. Check Render logs for Telegram errors
5. Redeploy if needed
```

---

### Issue: Service sleeps after 15 minutes
**Symptoms:** API works then becomes unresponsive
**Solutions:** This should NOT happen! Keep-alive is built-in
1. Verify render.yaml has health check
2. Check app.py has keep_alive() function
3. View logs for "Keep-alive ping sent"

**Fix:**
```
1. Check render.yaml syntax
2. Verify app.py has keep_alive thread
3. Check logs for "Keep-alive ping"
4. Redeploy if needed
```

---

### Issue: High error rate or crashes
**Symptoms:** 500 errors, service crashing
**Solutions:**
1. Check Python version compatibility
2. Verify dependencies in requirements.txt
3. Check file permissions
4. Review Render logs

**Fix:**
```
1. View Render logs in detail
2. Look for Python errors
3. Check requirements.txt
4. Redeploy clean version
```

---

### Issue: Database errors
**Symptoms:** "Database locked" or "No table" errors
**Solutions:**
1. SQLite auto-initializes
2. Check write permissions to /tmp
3. Verify db.py is present and correct

**Fix:**
```
1. Check core/db.py is correct
2. Verify /tmp is writable
3. Redeploy
4. For production: use PostgreSQL
```

---

## LOG ANALYSIS

### Where to Check Logs
```
Render Dashboard → Select Service → Logs tab
Real-time streaming logs appear
```

### What to Look For

**Good Signs:**
```
✓ "Keep-alive ping sent"
✓ "Starting gunicorn"
✓ "Application running"
✓ "Health check passed"
```

**Warning Signs:**
```
✗ "Error importing"
✗ "Module not found"
✗ "Connection refused"
✗ "Build failed"
```

### Common Log Messages

```
[Good] Application running on http://0.0.0.0:5000
[Good] Keep-alive ping sent ✓
[Good] Health check: status=healthy
[Warning] Build dependencies might be missing
[Error] ModuleNotFoundError: No module named 'core'
[Error] syntax error in Python file
[Error] database locked
```

---

## ROLLBACK/FIX STEPS

### If Something Goes Wrong

1. **Quick Fix (10 min)**
   ```
   1. Go to Render Dashboard
   2. Click "Redeploy"
   3. Wait 3-5 minutes
   4. Test again
   ```

2. **Configuration Fix (5 min)**
   ```
   1. Fix issue in GitHub
   2. Commit changes
   3. Render auto-redeploys
   4. Test again
   ```

3. **Full Rebuild (15 min)**
   ```
   1. Delete service on Render
   2. Create new service
   3. Re-deploy from GitHub
   4. Test again
   ```

---

## PERFORMANCE OPTIMIZATION

### Monitor CPU/Memory
- Render Dashboard → Metrics
- Green = Good
- Red = Needs optimization

### Optimize if Needed
1. Reduce MAX_CONCURRENT_PROCESSING
2. Upgrade Render plan
3. Add PostgreSQL for production
4. Cache results if possible

---

## SECURITY VERIFICATION

After deployment, verify:

```
✓ Admin panel password protected
✓ API key authentication working
✓ APK files deleted after processing
✓ HTTPS enabled (Render provides)
✓ Environment variables not exposed
✓ Database credentials protected
✓ Telegram token not in logs
```

---

## SUCCESS CRITERIA

All of these should work:

```
✓ https://your-service.onrender.com/health
  Returns: {"status": "healthy"}

✓ https://your-service.onrender.com/aryan
  Shows: Admin login page

✓ Login with 7949539794 / Vishal12
  Shows: Admin dashboard

✓ Create API key
  Works: New key generated

✓ Extract APK
  Returns: Firebase config

✓ Check Telegram channel
  Sees: Extraction result

✓ Check Render logs
  Shows: "Keep-alive ping sent ✓"

✓ Wait 15+ minutes
  API: Still works!
```

If ALL of these work → **DEPLOYMENT SUCCESSFUL! 🎉**

---

## FINAL CHECKLIST (Before Going Live)

- [ ] All tests pass
- [ ] API responding to requests
- [ ] Admin panel working
- [ ] Telegram integration working
- [ ] Keep-alive running (check logs)
- [ ] No errors in logs
- [ ] API keys can be created
- [ ] Quotas working
- [ ] APK extraction working
- [ ] Service doesn't sleep
- [ ] Performance is good
- [ ] Security features enabled

✅ **If all checked → You're DONE! 🚀**

---

## SUPPORT REFERENCE

| Issue | Check File |
|-------|-----------|
| General | COMPLETE_GUIDE.md |
| Quick help | QUICK_REFERENCE.md |
| Deployment | This file |
| API docs | COMPLETE_GUIDE.md → API ENDPOINTS |
| Code questions | See Python files |

---

**Good luck! You've got this!** 💪

Any issues? Follow this guide step by step.

---

Version: 1.0 | Last Updated: June 2026 | Status: Complete ✅
