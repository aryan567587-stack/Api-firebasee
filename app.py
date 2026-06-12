#!/usr/bin/env python3
"""
ARYAN FIREBASE API - PRODUCTION READY
With Render Keep-Alive Fix
"""

from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from functools import wraps
import os
import json
import hashlib
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import threading
from concurrent.futures import ThreadPoolExecutor
import requests

# Import our modules
from config import *
from core.db import init_db, get_db
from core.extractor import extract_firebase
from core.telegram import init_telegram, send_scan_result
import logging

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🚀 INITIALIZATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database
db = init_db()
tg_bot = init_telegram()

# Thread pool
executor = ThreadPoolExecutor(max_workers=MAX_CONCURRENT_PROCESSING)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🔐 AUTHENTICATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        if not api_key:
            return jsonify({"error": "Missing API Key", "code": 401}), 401
        
        # Check in database
        quota = db.get_quota(api_key)
        if quota is None or quota.get('banned'):
            return jsonify({"error": "Invalid or banned API Key", "code": 403}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🚀 ROUTES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.route('/')
def home():
    """API Home - Health Check"""
    return jsonify({
        "status": "healthy",
        "service": "Aryan Firebase API",
        "version": "1.0",
        "endpoints": {
            "extract": "POST /extract (with X-API-Key header + APK file)",
            "status": "GET /status (with X-API-Key header)",
            "admin": "GET /aryan (admin panel)",
            "health": "GET /health"
        }
    }), 200

@app.route('/health')
def health():
    """Health Check - Used by Render to detect if service is alive"""
    return jsonify({"status": "healthy"}), 200

@app.route('/ping')
def ping():
    """Keep-Alive Ping - Prevents Render auto-sleep"""
    return jsonify({"pong": True, "timestamp": datetime.now().isoformat()}), 200

@app.route('/extract', methods=['POST'])
@require_api_key
def extract_apk():
    """Main APK Extraction Endpoint"""
    try:
        # Check if file in request
        if 'apk' not in request.files:
            return jsonify({"error": "No APK file provided"}), 400
        
        file = request.files['apk']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Get API key
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        
        # Check quota
        quota = db.get_quota(api_key)
        if quota['remaining'] <= 0:
            return jsonify({"error": "Quota exceeded", "quota": quota}), 429
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract in background
        start_time = datetime.now()
        result = extract_firebase(filepath)
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Update quota
        db.increment_quota_usage(api_key)
        new_quota = db.get_quota(api_key)
        
        # Send to Telegram
        executor.submit(send_scan_result, {
            "apk_name": filename,
            "package": result.get('package', 'Unknown'),
            "firebase": result.get('firebase', {}),
            "api_key": api_key[:10] + "***",
            "timestamp": start_time.isoformat()
        }, tg_bot)
        
        # Delete APK file
        try:
            os.remove(filepath)
        except:
            pass
        
        # Return response
        return jsonify({
            "status": "success",
            "apk_name": filename,
            "package": result.get('package'),
            "firebase": result.get('firebase'),
            "processing_time_seconds": processing_time,
            "timestamp": start_time.isoformat(),
            "quota": {
                "used": new_quota['used'],
                "remaining": new_quota['remaining'],
                "max": new_quota['max']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Extract error: {str(e)}")
        return jsonify({"error": str(e), "code": 500}), 500

@app.route('/status')
@require_api_key
def status():
    """Check API Key Quota"""
    api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
    quota = db.get_quota(api_key)
    return jsonify(quota), 200

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🔐 ADMIN PANEL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.route('/aryan', methods=['GET', 'POST'])
def admin_login():
    """Admin Login Page"""
    if request.method == 'POST':
        admin_id = request.form.get('admin_id')
        password = request.form.get('password')
        
        if admin_id == ADMIN_ID and password == ADMIN_PASSWORD:
            session['admin_id'] = admin_id
            session.permanent = True
            app.permanent_session_lifetime = timedelta(hours=24)
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error="Invalid credentials"), 401
    
    return render_template('admin_login.html')

@app.route('/aryan/dashboard')
@admin_required
def admin_dashboard():
    """Admin Dashboard"""
    stats = db.get_stats()
    api_keys = db.get_all_api_keys()
    return render_template('admin_dashboard.html', stats=stats, api_keys=api_keys)

@app.route('/aryan/create_key', methods=['POST'])
@admin_required
def create_api_key():
    """Create new API key"""
    name = request.form.get('name', 'Unnamed')
    quota = int(request.form.get('quota', MAX_APK_QUOTA))
    
    api_key = f"aryan_{hashlib.sha256(os.urandom(32)).hexdigest()[:24]}"
    db.create_api_key(api_key, name, quota)
    
    return jsonify({"api_key": api_key, "name": name, "quota": quota}), 201

@app.route('/aryan/ban_key', methods=['POST'])
@admin_required
def ban_api_key():
    """Ban API key"""
    api_key = request.form.get('api_key')
    db.ban_api_key(api_key)
    return jsonify({"status": "banned"}), 200

@app.route('/aryan/logout')
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for('admin_login'))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🔄 KEEP-ALIVE MECHANISM (RENDER FIX)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def keep_alive():
    """Background thread to keep service alive on Render"""
    import time
    while True:
        try:
            time.sleep(600)  # Every 10 minutes
            # Self-ping to stay awake
            service_url = os.getenv('SERVICE_URL', 'http://localhost:5000')
            requests.get(f"{service_url}/ping", timeout=5)
            logger.info("Keep-alive ping sent ✓")
        except Exception as e:
            logger.warning(f"Keep-alive error: {e}")

# Start keep-alive thread
keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
keep_alive_thread.start()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🚀 RUN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == '__main__':
    app.run(
        host=API_HOST,
        port=API_PORT,
        debug=DEBUG,
        use_reloader=False
    )
