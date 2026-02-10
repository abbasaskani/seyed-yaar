"""
ایجاد گزارش کامل از تحلیل داده‌ها
"""

import json
import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

def create_analysis_report():
    """ایجاد گزارش تصویری و متنی"""
    
    print("📊 ایجاد گزارش تحلیل...")
    
    # پیدا کردن آخرین فایل نتایج
    results_dir = Path("results")
    json_files = list(results_dir.glob("*.json"))
    
    if not json_files:
        print("❌ فایل نتیجه‌ای یافت نشد")
        return
    
    latest_json = sorted(json_files)[-1]
    
    # خواندن نتایج
    with open(latest_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # ۱. ایجاد گزارش متنی
    create_text_report(data, latest_json)
    
    # ۲. ایجاد نمودار
    create_chart(data)
    
    print("✅ گزارش ایجاد شد!")

def create_text_report(data, json_file):
    """ایجاد گزارش متنی"""
    
    report_dir = Path("reports")
    report_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = report_dir / f"report_{timestamp}.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("🐟 گزارش تحلیل مناطق ماهی‌گیری ماهی تن\n")
        f.write("=" * 60 + "\n\n")
        
        f.write(f"📅 تاریخ تحلیل: {datetime.datetime.now().strftime('%Y/%m/%d %H:%M')}\n")
        f.write(f"📂 فایل داده: {json_file.name}\n\n")
        
        f.write("🌡️ آمار دمای سطح دریا:\n")
        f.write("-" * 40 + "\n")
        f.write(f"   حداقل دما: {data.get('min_temp', 0):.2f}°C\n")
        f.write(f"   حداکثر دما: {data.get('max_temp', 0):.2f}°C\n")
        f.write(f"   میانگین دما: {data.get('mean_temp', 0):.2f}°C\n\n")
        
        f.write("🔥 مناطق گرم (Hotspots):\n")
        f.write("-" * 40 + "\n")
        f.write(f"   تعداد مناطق گرم: {data.get('hotspot_count', 0):,} نقطه\n")
        f.write(f"   درصد مناطق گرم: {data.get('hotspot_percentage', 0):.1f}%\n\n")
        
        # تحلیل وضعیت
        f.write("🎯 تحلیل وضعیت ماهی‌گیری:\n")
        f.write("-" * 40 + "\n")
        
        hotspot_percent = data.get('hotspot_percentage', 0)
        
        if hotspot_percent > 20:
            f.write("✅ وضعیت: عالی\n")
            f.write("   شرایط بسیار مناسب برای ماهی‌گیری ماهی تن\n")
            f.write("   احتمال موفقیت بالا\n")
        elif hotspot_percent > 10:
            f.write("🟡 وضعیت: خوب\n")
            f.write("   شرایط نسبتاً مناسب\n")
            f.write("   نیاز به بررسی دقیق‌تر مناطق\n")
        else:
            f.write("🔴 وضعیت: متوسط\n")
            f.write("   شرایط چندان مطلوب نیست\n")
            f.write("   پیشنهاد: صبر برای روزهای آتی\n")
        
        f.write("\n" + "=" * 60 + "\n")
        f.write("📋 توصیه‌های عملی:\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("۱. بهترین زمان صید: ساعات اولیه صبح\n")
        f.write("۲. مناطق پیشنهادی: مناطق با دمای ۲۲-۲۸ درجه سانتی‌گراد\n")
        f.write("۳. تجهیزات پیشنهادی: قلاب‌های مخصوص ماهی تن\n")
        f.write("۴. ایمنی: بررسی شرایط جوی قبل از حرکت\n")
        
        f.write("\n" + "=" * 60 + "\n")
        f.write("⚠️ نکات مهم:\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("• این تحلیل بر اساس داده‌های دمای سطح دریا است\n")
        f.write("• عوامل دیگری مانند جریان‌های دریایی نیز مهم هستند\n")
        f.write("• همواره قوانین ماهی‌گیری منطقه را رعایت کنید\n")
        f.write("• داده‌ها از NOAA دریافت شده‌اند\n")
    
    print(f"📄 گزارش متنی ایجاد شد: {report_file}")

def create_chart(data):
    """ایجاد نمودار دمایی"""
    
    charts_dir = Path("charts")
    charts_dir.mkdir(exist_ok=True)
    
    # ایجاد داده برای نمودار
    labels = ['حداقل', 'میانگین', 'حداکثر']
    values = [
        data.get('min_temp', 0),
        data.get('mean_temp', 0),
        data.get('max_temp', 0)
    ]
    
    # رنگ‌ها بر اساس دما
    colors = []
    for val in values:
        if val < 15:
            colors.append('#3498db')  # آبی سرد
        elif val < 25:
            colors.append('#f1c40f')  # زرد گرم
        else:
            colors.append('#e74c3c')  # قرمز داغ
    
    # ایجاد نمودار
    plt.figure(figsize=(10, 6))
    bars = plt.bar(labels, values, color=colors, edgecolor='black')
    
    # اضافه کردن مقدار روی هر میله
    for bar, value in zip(bars, values):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{value:.1f}°C', ha='center', va='bottom', fontsize=12)
    
    plt.title('دمای سطح دریا - مناطق ماهی‌گیری', fontsize=16, fontname='B Nazanin', fontweight='bold')
    plt.ylabel('دما (°C)', fontsize=14, fontname='B Nazanin')
    plt.grid(axis='y', alpha=0.3)
    
    # اضافه کردن توضیحات
    plt.figtext(0.5, 0.01, 
               f'تعداد مناطق گرم: {data.get("hotspot_count", 0):,} نقطه | درصد مناطق گرم: {data.get("hotspot_percentage", 0):.1f}%',
               ha='center', fontsize=11, style='italic')
    
    # ذخیره نمودار
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    chart_file = charts_dir / f"temperature_chart_{timestamp}.png"
    plt.tight_layout()
    plt.savefig(chart_file, dpi=150)
    plt.close()
    
    print(f"📈 نمودار ایجاد شد: {chart_file}")

def create_daily_summary():
    """ایجاد خلاصه روزانه"""
    
    # جمع‌آوری همه نتایج
    results_dir = Path("results")
    json_files = list(results_dir.glob("*.json"))
    
    if len(json_files) < 2:
        print("⚠️ برای تحلیل روند نیاز به حداقل ۲ روز داده است")
        return
    
    # خواندن همه نتایج
    all_data = []
    dates = []
    
    for file in sorted(json_files)[-7:]:  # ۷ روز اخیر
        with open(file, 'r') as f:
            data = json.load(f)
            all_data.append(data)
            # استخراج تاریخ از نام فایل
            date_str = file.stem.split('_')[-1]
            dates.append(date_str)
    
    # ایجاد گزارش روند
    summary_dir = Path("trends")
    summary_dir.mkdir(exist_ok=True)
    
    summary_file = summary_dir / f"weekly_summary_{datetime.datetime.now().strftime('%Y%m%d')}.txt"
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("📈 تحلیل روند هفتگی مناطق ماهی‌گیری\n")
        f.write("=" * 50 + "\n\n")
        
        f.write("📊 تغییرات میانگین دما:\n")
        for i, (date, data) in enumerate(zip(dates[-5:], all_data[-5:])):
            f.write(f"   {date}: {data['mean_temp']:.1f}°C")
            if i > 0:
                change = data['mean_temp'] - all_data[i-1]['mean_temp']
                f.write(f" ({change:+.1f}°C)")
            f.write("\n")
        
        f.write(f"\n📈 روند مناطق گرم:\n")
        for i, (date, data) in enumerate(zip(dates[-5:], all_data[-5:])):
            f.write(f"   {date}: {data['hotspot_percentage']:.1f}%")
            if i > 0:
                change = data['hotspot_percentage'] - all_data[i-1]['hotspot_percentage']
                f.write(f" ({change:+.1f}%)")
            f.write("\n")
        
        f.write(f"\n🎯 پیش‌بینی فردا:\n")
        last_percent = all_data[-1]['hotspot_percentage']
        
        if last_percent > 20:
            f.write("   شرایط عالی ادامه خواهد داشت\n")
        elif last_percent > 15:
            f.write("   شرایط خوب - احتمال بهبود\n")
        else:
            f.write("   نیاز به بررسی بیشتر - احتمال تغییر\n")
    
    print(f"📈 گزارش روند ایجاد شد: {summary_file}")

if __name__ == "__main__":
    print("=" * 60)
    print("سیستم گزارش‌گیری پیشرفته")
    print("=" * 60)
    
    create_analysis_report()
    create_daily_summary()
    
    print("\n✅ همه گزارش‌ها ایجاد شدند!")
    print("📁 پوشه reports: گزارش‌های متنی")
    print("📁 پوشه charts: نمودارها")
    print("📁 پوشه trends: تحلیل روند")
    print("=" * 60)
