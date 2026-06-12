#!/usr/bin/env python3
"""
📱 Example Telegram Bot — Uses Aryan Firebase API

This bot:
1. Accepts APK files
2. Sends to Firebase extraction API
3. Shows progress
4. Returns Firebase config to user
"""

import telebot
import requests
import os
from datetime import datetime

# Config
BOT_TOKEN = "YOUR_BOT_TOKEN"
API_URL = "https://your-render-url.onrender.com"  # Change to your Render URL
API_KEY = "aryan_your_api_key_here"

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """
╔════════════════════════════════════╗
║      🔥 FIREBASE EXTRACTOR BOT     ║
║   Powered by Aryan API             ║
╚════════════════════════════════════╝

👇 *How to use:*

1. Send me any `.apk` file
2. I'll extract Firebase config
3. Results sent to company channel

*Supported:*
✅ Firebase Project ID
✅ API Keys
✅ Database URLs
✅ Storage Bucket
✅ And more...

📊 Quota: Check `/status`
    """
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(commands=['status'])
def check_status(message):
    try:
        headers = {'X-API-Key': API_KEY}
        response = requests.get(f"{API_URL}/status", headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()['quota']
            text = f"""
📊 *API Status*

Used: `{data['used']}/{data['max']}`
Remaining: `{data['remaining']}`

Recent scans: Check dashboard
            """
        else:
            text = "❌ API error"
        
        bot.reply_to(message, text, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(content_types=['document'])
def handle_apk(message):
    # Check if it's an APK
    file_info = bot.get_file(message.document.file_id)
    
    if not file_info.file_path.lower().endswith('.apk'):
        bot.reply_to(message, "⚠️ Please send an .apk file")
        return
    
    # Send progress message
    progress_msg = bot.reply_to(message, "⚙️ Processing...\n\n`[░░░░░░░░░░░░░░░░░░░░] 0%`", parse_mode="Markdown")
    
    try:
        # Download APK
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Save temp
        temp_path = f"/tmp/{message.document.file_name}"
        with open(temp_path, 'wb') as f:
            f.write(downloaded_file)
        
        # Update progress
        bot.edit_message_text(
            "⚙️ Processing...\n\n`[████░░░░░░░░░░░░░░░░] 25%`\n\n🔄 _Sending to API..._",
            message.chat.id, progress_msg.message_id, parse_mode="Markdown"
        )
        
        # Send to API
        with open(temp_path, 'rb') as f:
            files = {'apk': f}
            headers = {'X-API-Key': API_KEY}
            
            response = requests.post(
                f"{API_URL}/extract",
                files=files,
                headers=headers,
                timeout=120
            )
        
        # Clean up
        os.remove(temp_path)
        
        if response.status_code != 200:
            bot.edit_message_text(
                f"❌ Error: {response.json().get('error', 'Unknown error')}",
                message.chat.id, progress_msg.message_id, parse_mode="Markdown"
            )
            return
        
        # Update progress
        bot.edit_message_text(
            "⚙️ Processing...\n\n`[████████████████░░░░] 75%`\n\n💾 _Formatting results..._",
            message.chat.id, progress_msg.message_id, parse_mode="Markdown"
        )
        
        # Format result
        data = response.json()
        firebase = data.get('firebase', {})
        
        result_text = f"""
╔════════════════════════════════════╗
║     ✅ EXTRACTION SUCCESSFUL       ║
╚════════════════════════════════════╝

📦 *APK:* `{data['apk_name']}`
📍 *Package:* `{data['package']}`

🔥 *Firebase Config:*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🆔 *Project ID:*
`{firebase.get('project_id', 'N/A')}`

🔑 *API Key:*
`{firebase.get('api_key', 'N/A')[:50]}...`

📱 *App ID:*
`{firebase.get('app_id', 'N/A')}`

💾 *DB URL:*
`{firebase.get('db_url', 'N/A')}`

☁️ *Storage Bucket:*
`{firebase.get('storage_bucket', 'N/A')}`

📤 *Sender ID:*
`{firebase.get('sender_id', 'N/A')}`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏱️ *Processing Time:* {data['processing_time_seconds']}s
👤 *Uploaded by:* {data['uploaded_by']}
📅 *Time:* {data['timestamp'][:19]}

📊 *Quota Remaining:* {data['quota']['remaining']}/{data['quota']['max']}
        """
        
        bot.edit_message_text(
            result_text,
            message.chat.id, progress_msg.message_id, parse_mode="Markdown"
        )
        
    except Exception as e:
        bot.edit_message_text(
            f"❌ Error: {str(e)}",
            message.chat.id, progress_msg.message_id, parse_mode="Markdown"
        )

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    bot.reply_to(message, "📤 Send me an .apk file to extract Firebase config!")

if __name__ == '__main__':
    print("🤖 Bot starting...")
    bot.infinity_polling()
