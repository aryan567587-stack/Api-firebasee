#!/usr/bin/env python3
"""
╔══════════════════════════════════════════╗
║        ARYAN FIREBASE API - CONFIG       ║
║          Render Deployment Ready         ║
╚══════════════════════════════════════════╝
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🔐 SECURITY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Admin Panel Login
ADMIN_ID = "7949539794"
ADMIN_PASSWORD = "Vishal12"
SECRET_KEY = "Ctrl"  # For session encryption

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  📱 TELEGRAM
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "8725165662:AAFs_sfh50zGXW7Y6ZT1dNV488HN-q4Vieo")
TG_CHANNEL_ID = os.getenv("TG_CHANNEL_ID", "-1003694677261")  # Group/Channel where results go
TG_ADMIN_ID = 7949539794

# Uploaded by (branding)
UPLOADED_BY = "@Aryan_babu99"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  📊 QUOTAS & LIMITS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MAX_APK_QUOTA = 2000  # Max APKs per API key
MAX_CONCURRENT_PROCESSING = 100  # Process 100 APKs simultaneously
APK_CLEANUP_DELAY = 2  # Seconds — instant delete after processing
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB max APK size

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🗄️  DATABASE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Render uses ephemeral file system — use environment database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///aryan.db")  # or PostgreSQL

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🌐 API
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

API_HOST = "0.0.0.0"
API_PORT = int(os.getenv("PORT", 5000))
DEBUG = os.getenv("DEBUG", "False") == "True"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  📁 STORAGE (Render)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

UPLOAD_FOLDER = "/tmp/aryan_uploads"  # Render ephemeral storage
RESULTS_FOLDER = "/tmp/aryan_results"

import os
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🔧 TOOLS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AAPT_PATH = os.getenv("AAPT_PATH", "/usr/bin/aapt")  # Android Asset Packaging Tool
