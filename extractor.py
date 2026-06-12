#!/usr/bin/env python3
"""
Firebase config extractor from APK
Uses aapt (Android Asset Packaging Tool)
"""

import subprocess
import json
import re
import os
import tempfile
import zipfile
from pathlib import Path
from datetime import datetime
import time

class FirebaseExtractor:
    def __init__(self):
        self.aapt_path = "/usr/bin/aapt"  # Debian/Ubuntu
        self._check_aapt()
    
    def _check_aapt(self):
        """Ensure aapt is available"""
        try:
            subprocess.run([self.aapt_path, "version"], 
                          capture_output=True, timeout=5)
        except:
            print("⚠️ aapt not found. Install: apt-get install aapt")
    
    def extract_apk_info(self, apk_path):
        """Extract basic APK info"""
        try:
            result = subprocess.run(
                [self.aapt_path, "dump", "badging", apk_path],
                capture_output=True, text=True, timeout=30
            )
            
            info = {}
            for line in result.stdout.split('\n'):
                if line.startswith("package:"):
                    match = re.search(r"name='([^']+)'", line)
                    if match:
                        info['package'] = match.group(1)
                if line.startswith("versionName="):
                    match = re.search(r"versionName='([^']+)'", line)
                    if match:
                        info['version'] = match.group(1)
            
            return info
        except Exception as e:
            return {'error': str(e)}
    
    def extract_firebase_config(self, apk_path):
        """Extract Firebase config from AndroidManifest.xml or google-services.json"""
        firebase_config = {
            'project_id': None,
            'api_key': None,
            'app_id': None,
            'db_url': None,
            'storage_bucket': None,
            'sender_id': None,
            'auth_required': False
        }
        
        try:
            # Method 1: Extract google-services.json from APK
            with zipfile.ZipFile(apk_path, 'r') as zip_ref:
                # Common paths
                paths_to_check = [
                    'assets/google-services.json',
                    'res/values/google-services.xml',
                    'assets/firebase-config.json'
                ]
                
                for path in paths_to_check:
                    try:
                        if path in zip_ref.namelist():
                            content = zip_ref.read(path).decode('utf-8')
                            
                            if path.endswith('.json'):
                                config = json.loads(content)
                                firebase_config.update(self._parse_google_services_json(config))
                            else:
                                firebase_config.update(self._parse_xml_config(content))
                            
                            break
                    except:
                        continue
            
            # Method 2: Extract from AndroidManifest.xml metadata
            manifest_data = self._extract_manifest_meta(apk_path)
            if manifest_data:
                firebase_config.update(manifest_data)
            
            # Clean null values
            firebase_config = {k: v for k, v in firebase_config.items() if v is not None}
            
            return firebase_config
        
        except Exception as e:
            return {'error': str(e), 'auth_required': True}
    
    def _parse_google_services_json(self, config):
        """Parse google-services.json structure"""
        extracted = {}
        
        try:
            # Standard structure
            if 'project_info' in config:
                proj = config['project_info']
                extracted['project_id'] = proj.get('project_id')
                extracted['project_number'] = proj.get('project_number')
            
            if 'client' in config and config['client']:
                client = config['client'][0]
                
                if 'client_info' in client:
                    extracted['app_id'] = client['client_info'].get('mobilesdk_app_id')
                    extracted['package'] = client['client_info'].get('android_client_info', {}).get('package_name')
                
                if 'api_key' in client:
                    api_keys = client['api_key']
                    if api_keys:
                        extracted['api_key'] = api_keys[0].get('current_key')
            
            if 'configuration_version' in config:
                extracted['config_version'] = config['configuration_version']
        
        except:
            pass
        
        return extracted
    
    def _parse_xml_config(self, xml_content):
        """Parse XML-based Firebase config"""
        extracted = {}
        
        # Regex patterns
        patterns = {
            'project_id': r'<string[^>]*name="firebase_project_id"[^>]*>([^<]+)</string>',
            'api_key': r'<string[^>]*name="firebase_api_key"[^>]*>([^<]+)</string>',
            'app_id': r'<string[^>]*name="firebase_app_id"[^>]*>([^<]+)</string>',
            'db_url': r'<string[^>]*name="firebase_database_url"[^>]*>([^<]+)</string>',
            'storage_bucket': r'<string[^>]*name="firebase_storage_bucket"[^>]*>([^<]+)</string>',
            'sender_id': r'<string[^>]*name="gcm_sender_id"[^>]*>([^<]+)</string>',
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, xml_content)
            if match:
                extracted[key] = match.group(1)
        
        return extracted
    
    def _extract_manifest_meta(self, apk_path):
        """Extract metadata from AndroidManifest.xml"""
        extracted = {}
        
        try:
            with zipfile.ZipFile(apk_path, 'r') as zip_ref:
                if 'AndroidManifest.xml' in zip_ref.namelist():
                    manifest = zip_ref.read('AndroidManifest.xml')
                    # Binary XML parsing (simplified)
                    # For full parsing, use external library
                    if b'firebase_project_id' in manifest:
                        extracted['firebase_detected'] = True
        except:
            pass
        
        return extracted
    
    def process_apk(self, apk_path, timeout=60):
        """Full APK processing with timeout"""
        start_time = time.time()
        
        try:
            # Validate APK
            if not zipfile.is_zipfile(apk_path):
                return None, "Invalid APK file", time.time() - start_time
            
            # Extract info
            apk_info = self.extract_apk_info(apk_path)
            firebase_config = self.extract_firebase_config(apk_path)
            
            result = {
                **apk_info,
                'firebase': firebase_config
            }
            
            processing_time = time.time() - start_time
            return result, None, processing_time
        
        except subprocess.TimeoutExpired:
            return None, "Processing timeout (>60s)", 60.0
        except Exception as e:
            return None, str(e), time.time() - start_time


# Global extractor
extractor = FirebaseExtractor()

def extract_firebase(apk_path):
    """Convenience function"""
    return extractor.process_apk(apk_path)
