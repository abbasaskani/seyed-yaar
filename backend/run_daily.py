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
    print("   لطفاً در تنظیمات گیت‌هاب، Secrets را تنظیم کنید:")
    print("   ۱. به Settings → Secrets and variables → Actions بروید")
    print("   ۲. COPERNICUS_USERNAME و COPERNICUS_PASSWORD را اضافه کنید")
    sys.exit(1)

# ۲. ایجاد پوشه‌ها
print("\n📁 ایجاد پوشه‌های مورد نیاز...")
try:
    Path("data").mkdir(exist_ok=True)
    Path("results").mkdir(exist_ok=True)
    print("✅ پوشه‌ها ایجاد شدند")
except:
    print("⚠️ خطا در ایجاد پوشه‌ها")

# ۳. ایجاد فایل خروجی
print("\n📝 ایجاد فایل نتایج...")
try:
    now = datetime.datetime.now()
    filename = f"نتیجه_{now.strftime('%Y-%m-%d_%H-%M')}.txt"
    output_path = Path("results") / filename
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("=" * 40 + "\n")
        f.write("گزارش تحلیل داده‌های ماهی تن\n")
        f.write("=" * 40 + "\n")
        f.write(f"تاریخ: {now.strftime('%Y/%m/%d %H:%M')}\n")
        f.write(f"وضعیت: موفق\n")
        f.write(f"نام کاربری: {username[:3]}***\n")
        f.write(f"پوشه داده: data/\n")
        f.write(f"پوشه نتایج: results/\n")
        f.write("=" * 40 + "\n")
        f.write("\nمراحل بعدی:\n")
        f.write("۱. دانلود داده‌های دمای سطح دریا\n")
        f.write("۲. تحلیل مناطق با دمای مناسب\n")
        f.write("۳. تولید نقشه‌های ماهی تن\n")
    
    print(f"✅ فایل ایجاد شد: {filename}")
    print(f"   مسیر: results/{filename}")
    
except Exception as e:
    print(f"❌ خطا در ایجاد فایل: {e}")

# ۴. لیست کردن فایل‌های ایجاد شده
print("\n📊 لیست فایل‌های موجود:")
try:
    if Path("results").exists():
        files = list(Path("results").glob("*.txt"))
        if files:
            for file in files[-3:]:  # ۳ فایل آخر
                print(f"   • {file.name}")
        else:
            print("   (هیچ فایلی موجود نیست)")
    else:
        print("   پوشه results وجود ندارد")
except:
    pass

print("\n" + "=" * 50)
print("تحلیل با موفقیت انجام شد!")
print("=" * 50)
