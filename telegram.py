#!/usr/bin/env python3
"""
Telegram Bot Integration — sends scan results to channel
"""

import asyncio
import json
import aiohttp
from datetime import datetime
from config import TG_BOT_TOKEN, TG_CHANNEL_ID, UPLOADED_BY

class TelegramBot:
    def __init__(self):
        self.token = TG_BOT_TOKEN
        self.channel_id = TG_CHANNEL_ID
        self.api_url = f"https://api.telegram.org/bot{self.token}"
    
    async def send_result(self, result_data, apk_filename):
        """Send scan result to Telegram channel"""
        
        message_text = self._format_result(result_data, apk_filename)
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    'chat_id': self.channel_id,
                    'text': message_text,
                    'parse_mode': 'HTML',
                    'disable_web_page_preview': True
                }
                
                async with session.post(
                    f"{self.api_url}/sendMessage",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        return True, "✅ Sent to Telegram"
                    else:
                        text = await resp.text()
                        return False, f"Telegram error: {text}"
        
        except asyncio.TimeoutError:
            return False, "Telegram timeout"
        except Exception as e:
            return False, f"Telegram error: {str(e)}"
    
    def _format_result(self, result_data, apk_filename):
        """Format result as Telegram message"""
        
        firebase = result_data.get('firebase', {})
        package = result_data.get('package', 'Unknown')
        
        # Build message
        lines = [
            "╔════════════════════════════════════╗",
            "║     📱 FIREBASE CONFIG EXTRACTED    ║",
            "╚════════════════════════════════════╝",
            "",
            f"<b>📦 APK:</b> <code>{apk_filename}</code>",
            f"<b>📍 Package:</b> <code>{package}</code>",
            "",
            "<b>🔥 Firebase Configuration:</b>",
        ]
        
        # Firebase details
        config_items = [
            ('project_id', '🆔 Project ID'),
            ('api_key', '🔑 API Key'),
            ('app_id', '📱 App ID'),
            ('db_url', '💾 Database URL'),
            ('storage_bucket', '☁️ Storage Bucket'),
            ('sender_id', '📤 Sender ID'),
        ]
        
        for key, label in config_items:
            value = firebase.get(key)
            if value:
                # Truncate long values
                display_value = value[:50] + "..." if len(str(value)) > 50 else value
                lines.append(f"{label}: <code>{display_value}</code>")
            else:
                lines.append(f"{label}: <code>null</code>")
        
        # Footer
        lines.extend([
            "",
            "<b>📊 Metadata:</b>",
            f"Version: {result_data.get('version', 'Unknown')}",
            f"Uploaded by: {UPLOADED_BY}",
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        ])
        
        return "\n".join(lines)
    
    async def send_error_log(self, error_msg, apk_filename):
        """Send error to admin"""
        message = (
            f"❌ <b>EXTRACTION FAILED</b>\n\n"
            f"<b>APK:</b> <code>{apk_filename}</code>\n"
            f"<b>Error:</b> <code>{error_msg}</code>\n"
            f"<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    'chat_id': self.channel_id,
                    'text': message,
                    'parse_mode': 'HTML'
                }
                
                async with session.post(
                    f"{self.api_url}/sendMessage",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    return resp.status == 200
        except:
            return False


# Global instance
tg_bot = None

def init_telegram():
    global tg_bot
    tg_bot = TelegramBot()
    return tg_bot

def get_tg_bot():
    global tg_bot
    if tg_bot is None:
        init_telegram()
    return tg_bot

async def send_scan_result(result_data, apk_filename):
    """Async wrapper"""
    bot = get_tg_bot()
    return await bot.send_result(result_data, apk_filename)
