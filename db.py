#!/usr/bin/env python3
"""
Database layer — SQLite for Render (can upgrade to PostgreSQL)
"""

import sqlite3
import json
import threading
from datetime import datetime
from pathlib import Path

class Database:
    def __init__(self, db_path=":memory:"):
        self.db_path = db_path
        self.lock = threading.RLock()
        self._init_db()
    
    def _get_conn(self):
        """Thread-safe connection"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_db(self):
        """Create tables"""
        with self.lock:
            conn = self._get_conn()
            c = conn.cursor()
            
            # API Keys & Quotas
            c.execute('''CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY,
                api_key TEXT UNIQUE NOT NULL,
                owner_id TEXT,
                quota_used INTEGER DEFAULT 0,
                quota_max INTEGER DEFAULT 2000,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP,
                active BOOLEAN DEFAULT 1
            )''')
            
            # APK Processing Records
            c.execute('''CREATE TABLE IF NOT EXISTS apk_scans (
                id INTEGER PRIMARY KEY,
                api_key TEXT,
                apk_name TEXT,
                package_name TEXT,
                firebase_config TEXT,
                processing_time REAL,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deleted_at TIMESTAMP,
                FOREIGN KEY(api_key) REFERENCES api_keys(api_key)
            )''')
            
            # Admin Activity Log
            c.execute('''CREATE TABLE IF NOT EXISTS admin_log (
                id INTEGER PRIMARY KEY,
                admin_id TEXT,
                action TEXT,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            # Bot Connection Status
            c.execute('''CREATE TABLE IF NOT EXISTS bot_stats (
                id INTEGER PRIMARY KEY,
                bot_token TEXT UNIQUE,
                connected_at TIMESTAMP,
                last_heartbeat TIMESTAMP,
                status TEXT
            )''')
            
            conn.commit()
            conn.close()
    
    # ─── API Key Management ───
    def create_api_key(self, owner_id, quota_max=2000):
        import secrets
        api_key = f"aryan_{secrets.token_hex(16)}"
        
        with self.lock:
            conn = self._get_conn()
            c = conn.cursor()
            c.execute('''INSERT INTO api_keys 
                        (api_key, owner_id, quota_max) 
                        VALUES (?, ?, ?)''',
                      (api_key, owner_id, quota_max))
            conn.commit()
            conn.close()
        
        return api_key
    
    def get_api_key_info(self, api_key):
        with self.lock:
            conn = self._get_conn()
            c = conn.cursor()
            c.execute('SELECT * FROM api_keys WHERE api_key = ?', (api_key,))
            result = c.fetchone()
            conn.close()
            return dict(result) if result else None
    
    def check_quota(self, api_key):
        """Returns (used, remaining, is_available)"""
        info = self.get_api_key_info(api_key)
        if not info:
            return (0, 0, False)
        
        used = info['quota_used']
        max_q = info['quota_max']
        remaining = max_q - used
        
        return (used, remaining, remaining > 0)
    
    def increment_quota(self, api_key):
        """Use one quota"""
        with self.lock:
            conn = self._get_conn()
            c = conn.cursor()
            c.execute('''UPDATE api_keys 
                        SET quota_used = quota_used + 1, last_used = CURRENT_TIMESTAMP
                        WHERE api_key = ?''', (api_key,))
            conn.commit()
            conn.close()
    
    def set_quota_limit(self, api_key, new_limit):
        """Admin: change quota"""
        with self.lock:
            conn = self._get_conn()
            c = conn.cursor()
            c.execute('''UPDATE api_keys SET quota_max = ? WHERE api_key = ?''',
                      (new_limit, api_key))
            conn.commit()
            conn.close()
    
    def ban_api_key(self, api_key):
        with self.lock:
            conn = self._get_conn()
            c = conn.cursor()
            c.execute('UPDATE api_keys SET active = 0 WHERE api_key = ?', (api_key,))
            conn.commit()
            conn.close()
    
    def unban_api_key(self, api_key):
        with self.lock:
            conn = self._get_conn()
            c = conn.cursor()
            c.execute('UPDATE api_keys SET active = 1 WHERE api_key = ?', (api_key,))
            conn.commit()
            conn.close()
    
    def list_all_api_keys(self):
        """Admin: list all keys"""
        with self.lock:
            conn = self._get_conn()
            c = conn.cursor()
            c.execute('SELECT api_key, owner_id, quota_used, quota_max, active FROM api_keys')
            results = [dict(row) for row in c.fetchall()]
            conn.close()
        return results
    
    # ─── APK Scan Records ───
    def record_scan(self, api_key, apk_name, package_name, firebase_config, processing_time):
        """Log successful scan"""
        with self.lock:
            conn = self._get_conn()
            c = conn.cursor()
            c.execute('''INSERT INTO apk_scans 
                        (api_key, apk_name, package_name, firebase_config, processing_time, status)
                        VALUES (?, ?, ?, ?, ?, ?)''',
                      (api_key, apk_name, package_name, 
                       json.dumps(firebase_config), processing_time, 'success'))
            conn.commit()
            conn.close()
    
    def auto_delete_scan(self, scan_id):
        """Mark as deleted (Render auto-cleanup)"""
        with self.lock:
            conn = self._get_conn()
            c = conn.cursor()
            c.execute('''UPDATE apk_scans SET deleted_at = CURRENT_TIMESTAMP 
                        WHERE id = ?''', (scan_id,))
            conn.commit()
            conn.close()
    
    def get_scan_history(self, api_key=None, limit=100):
        """Get scan records"""
        with self.lock:
            conn = self._get_conn()
            c = conn.cursor()
            if api_key:
                c.execute('''SELECT id, apk_name, package_name, processing_time, created_at 
                            FROM apk_scans WHERE api_key = ? AND deleted_at IS NULL
                            ORDER BY created_at DESC LIMIT ?''', (api_key, limit))
            else:
                c.execute('''SELECT id, apk_name, package_name, processing_time, created_at 
                            FROM apk_scans WHERE deleted_at IS NULL
                            ORDER BY created_at DESC LIMIT ?''', (limit,))
            results = [dict(row) for row in c.fetchall()]
            conn.close()
        return results
    
    # ─── Statistics ───
    def get_stats(self):
        """Dashboard stats"""
        with self.lock:
            conn = self._get_conn()
            c = conn.cursor()
            
            # Total scans
            c.execute('SELECT COUNT(*) as count FROM apk_scans WHERE deleted_at IS NULL')
            total_scans = c.fetchone()['count']
            
            # Today's scans
            c.execute('''SELECT COUNT(*) as count FROM apk_scans 
                        WHERE deleted_at IS NULL 
                        AND DATE(created_at) = DATE('now')''')
            today_scans = c.fetchone()['count']
            
            # Active API keys
            c.execute('SELECT COUNT(*) as count FROM api_keys WHERE active = 1')
            active_keys = c.fetchone()['count']
            
            # Connected bots
            c.execute('SELECT COUNT(*) as count FROM bot_stats WHERE status = "connected"')
            connected_bots = c.fetchone()['count']
            
            conn.close()
        
        return {
            'total_scans': total_scans,
            'today_scans': today_scans,
            'active_api_keys': active_keys,
            'connected_bots': connected_bots
        }
    
    # ─── Admin Log ───
    def log_admin_action(self, admin_id, action, details=""):
        with self.lock:
            conn = self._get_conn()
            c = conn.cursor()
            c.execute('''INSERT INTO admin_log (admin_id, action, details)
                        VALUES (?, ?, ?)''', (admin_id, action, details))
            conn.commit()
            conn.close()
    
    def get_admin_log(self, limit=50):
        with self.lock:
            conn = self._get_conn()
            c = conn.cursor()
            c.execute('''SELECT * FROM admin_log 
                        ORDER BY timestamp DESC LIMIT ?''', (limit,))
            results = [dict(row) for row in c.fetchall()]
            conn.close()
        return results


# Global DB instance
db = None

def init_db(db_path="aryan.db"):
    global db
    db = Database(db_path)
    return db

def get_db():
    global db
    if db is None:
        init_db()
    return db
