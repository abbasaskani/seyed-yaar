"""
تست ساده اتصال به Copernicus
"""

import os
import requests
from requests.auth import HTTPBasicAuth

# گرفتن credentials از محیط
username = os.getenv("COPERNICUS_USERNAME")
password = os.getenv("COPERNICUS_PASSWORD")

print("🔍 تست اتصال به Copernicus Marine...")
print(f"Username: {username[:3]}***")
print(f"Password: {'*' * len(password) if password else 'Not found'}")

# تست با یک درخواست ساده
test_url = "https://my.cmems-du.eu/thredds/catalog.xml"

try:
    response = requests.get(test_url, auth=HTTPBasicAuth(username, password))
    print(f"\n📡 وضعیت اتصال: HTTP {response.status_code}")
    
    if response.status_code == 200:
        print("✅ اتصال موفق!")
        print(f"   سرور پاسخ داد: {len(response.text)} کاراکتر")
    else:
        print("❌ مشکل در اتصال")
        print(f"   پیام: {response.text[:100]}")
        
except Exception as e:
    print(f"❌ خطا: {e}")
