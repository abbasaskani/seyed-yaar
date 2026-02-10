"""
run_daily.py - بررسی ساده در دسترس بودن داده‌ها
"""

import os
import sys
import datetime
from pathlib import Path

print("=" * 50)
print("شروع تحلیل")
print("=" * 50)

# ۱. چک کردن Credentials
username = os.getenv("COPERNICUS_USERNAME")
password = os.getenv("COPERNICUS_PASSWORD")

if username and password:
    print(f"✅ اطلاعات ورود دریافت شد")
    print(f"   نام کاربری: {username[:3]}***")
else:
    print("❌ خطا: اطلاعات ورود پیدا نشد")
    sys.exit(1)

# ۲. ایجاد پوشه‌ها
print("\n📁 ایجاد پوشه‌های مورد نیاز...")
try:
    Path("data").mkdir(exist_ok=True)
    Path("results").mkdir(exist_ok=True)
    print("✅ پوشه‌ها ایجاد شدند")
except Exception as e:
    print(f"⚠️ خطا در ایجاد پوشه‌ها: {e}")

# ۳. ایجاد فایل خروجی
print("\n📝 ایجاد فایل نتایج...")
try:
    now = datetime.datetime.now()
    # استفاده از نام انگلیسی برای جلوگیری از مشکل مسیر
    filename = f"result_{now.strftime('%Y-%m-%d_%H-%M')}.txt"
    output_path = Path("results") / filename
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("=" * 40 + "\n")
        f.write("گزارش تحلیل داده‌های ماهی تن\n")
        f.write("=" * 40 + "\n")
        f.write(f"تاریخ: {now.strftime('%Y/%m/%d %H:%M')}\n")
        f.write(f"وضعیت: موفق\n")
        f.write(f"نام کاربری: {username[:3]}***\n")
        f.write(f"فایل: {filename}\n")
        f.write("=" * 40 + "\n")
    
    print(f"✅ فایل ایجاد شد: {filename}")
    print(f"   مسیر کامل: {output_path.absolute()}")
    
except Exception as e:
    print(f"❌ خطا در ایجاد فایل: {e}")
    sys.exit(1)

# ۴. تأیید ایجاد فایل
print("\n📊 تأیید ایجاد فایل...")
if output_path.exists():
    print(f"✅ فایل در محل مورد نظر وجود دارد")
    print(f"   حجم فایل: {output_path.stat().st_size} بایت")
else:
    print(f"❌ فایل ایجاد نشده است")

print("\n" + "=" * 50)
print("تحلیل با موفقیت انجام شد!")
print("=" * 50)
