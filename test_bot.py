#!/usr/bin/env python3
"""
Test Bot Script - Debug Telegram Bot Issues
"""
import requests
import sys

def test_bot():
    bot_token = "8412305939:AAHope2kwVNqKG2im-SdIAwVEN5LsWPSc-M"
    chat_id = "67943804"
    
    print("🤖 Testing Bot Connection...")
    print(f"Bot Token: {bot_token[:20]}...")
    print(f"Chat ID: {chat_id}")
    print()
    
    # Test 1: Check bot info
    print("1. Checking bot info...")
    try:
        response = requests.get(f"https://api.telegram.org/bot{bot_token}/getMe", timeout=10)
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info.get('ok'):
                result = bot_info['result']
                print(f"   ✅ Bot Name: {result.get('first_name', 'Unknown')}")
                print(f"   ✅ Username: {result.get('username', 'Unknown')}")
                print(f"   ✅ Can read groups: {result.get('can_read_all_group_messages', False)}")
        else:
            print(f"   ❌ Bot info error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 2: Try to send message
    print("2. Testing message sending...")
    try:
        telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        message_data = {
            'chat_id': chat_id,
            'text': '🧪 Test from Bot Manager - Debug script',
            'disable_web_page_preview': False
        }
        
        response = requests.post(telegram_url, json=message_data, timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("   ✅ Message sent successfully!")
                print(f"   Message ID: {result.get('result', {}).get('message_id', 'Unknown')}")
            else:
                error = result.get('description', 'Unknown error')
                print(f"   ❌ Telegram API error: {error}")
        else:
            print(f"   ❌ HTTP Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print()
    print("🔧 Solutions:")
    print("1. Make sure bot privacy is OFF (BotFather → Bot Settings → Group Privacy)")
    print("2. Send a message to the bot first from Telegram")
    print("3. Check if bot is admin in the chat/group")
    print("4. Verify chat ID format (private chats use positive numbers)")

if __name__ == "__main__":
    test_bot()
