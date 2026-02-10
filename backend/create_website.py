"""
ایجاد وب‌سایت کامل با نقشه و نمودار
"""

from pathlib import Path
import json
import datetime
import shutil

def create_advanced_website():
    """ایجاد وب‌سایت کامل"""
    
    print("🌐 ایجاد وب‌سایت پیشرفته...")
    
    # پیدا کردن آخرین نتایج
    results_dir = Path("results")
    json_files = list(results_dir.glob("*.json"))
    
    if not json_files:
        print("❌ فایل نتیجه‌ای یافت نشد")
        return
    
    latest_json = sorted(json_files)[-1]
    
    with open(latest_json, 'r') as f:
        data = json.load(f)
    
    # پیدا کردن آخرین نمودار
    charts_dir = Path("charts")
    png_files = list(charts_dir.glob("*.png"))
    chart_file = sorted(png_files)[-1] if png_files else None
    
    # پیدا کردن آخرین گزارش
    reports_dir = Path("reports")
    txt_files = list(reports_dir.glob("*.txt"))
    report_file = sorted(txt_files)[-1] if txt_files else None
    
    # کپی کردن نمودار به پوشه وب‌سایت
    website_dir = Path("website")
    website_dir.mkdir(exist_ok=True)
    
    if chart_file:
        shutil.copy(chart_file, website_dir / "chart.png")
    
    # ایجاد HTML کامل
    html_content = f'''
<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>سیستم تحلیل ماهی‌گیری ماهی تن</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{
            --primary: #0066cc;
            --secondary: #00aaff;
            --success: #28a745;
            --warning: #ffc107;
            --danger: #dc3545;
            --light: #f8f9fa;
            --dark: #343a40;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.8;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        header {{
            background: white;
            padding: 30px;
            border-radius: 15px 15px 0 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
            margin-bottom: 20px;
        }}
        
        h1 {{
            color: var(--primary);
            font-size: 2.5rem;
            margin-bottom: 10px;
        }}
        
        .tagline {{
            color: var(--secondary);
            font-size: 1.2rem;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.2);
        }}
        
        .stat-icon {{
            font-size: 2.5rem;
            color: var(--primary);
            margin-bottom: 15px;
        }}
        
        .stat-value {{
            font-size: 2rem;
            font-weight: bold;
            color: var(--dark);
            margin: 10px 0;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 1rem;
        }}
        
        .main-content {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }}
        
        @media (max-width: 768px) {{
            .main-content {{
                grid-template-columns: 1fr;
            }}
        }}
        
        .card {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .chart-container img {{
            width: 100%;
            border-radius: 10px;
        }}
        
        .recommendation {{
            background: linear-gradient(135deg, var(--warning) 0%, #ff9f43 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 30px;
        }}
        
        .recommendation h3 {{
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 8px 20px;
            border-radius: 50px;
            font-weight: bold;
            margin-top: 15px;
        }}
        
        .status-excellent {{
            background: var(--success);
            color: white;
        }}
        
        .status-good {{
            background: var(--warning);
            color: var(--dark);
        }}
        
        .status-average {{
            background: var(--danger);
            color: white;
        }}
        
        footer {{
            text-align: center;
            color: white;
            padding: 20px;
            margin-top: 30px;
        }}
        
        .update-time {{
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 10px;
            display: inline-block;
            margin-top: 15px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1><i class="fas fa-fish"></i> سیستم تحلیل ماهی‌گیری ماهی تن</h1>
            <p class="tagline">تحلیل هوشمند مناطق دریایی برای صیادان ماهی تن</p>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="fas fa-thermometer-half"></i>
                </div>
                <div class="stat-value">{data.get('mean_temp', 0):.1f}°C</div>
                <div class="stat-label">میانگین دمای سطح دریا</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="fas fa-fire"></i>
                </div>
                <div class="stat-value">{data.get('hotspot_count', 0):,}</div>
                <div class="stat-label">تعداد مناطق گرم شناسایی شده</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="fas fa-chart-line"></i>
                </div>
                <div class="stat-value">{data.get('hotspot_percentage', 0):.1f}%</div>
                <div class="stat-label">درصد مناطق گرم</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="fas fa-water"></i>
                </div>
                <div class="stat-value">{data.get('max_temp', 0):.1f}°C</div>
                <div class="stat-label">حداکثر دمای ثبت شده</div>
            </div>
        </div>
        
        <div class="recommendation">
            <h3><i class="fas fa-bullhorn"></i> توصیه امروز برای صیادان</h3>
            <p>
    '''
    
    # توصیه بر اساس درصد مناطق گرم
    hotspot_percent = data.get('hotspot_percentage', 0)
    
    if hotspot_percent > 20:
        html_content += '''
                <strong>شرایط عالی برای ماهی‌گیری!</strong>
                <br>امروز مناطق گرم زیادی شناسایی شده‌اند. بهترین زمان برای صید ماهی تن است.
                <br>مناطق با دمای ۲۴-۲۸ درجه سانتی‌گراد را هدف قرار دهید.
        '''
        status_class = "status-excellent"
        status_text = "شرایط عالی"
    elif hotspot_percent > 10:
        html_content += '''
                <strong>شرایط خوب برای ماهی‌گیری</strong>
                <br>مناطق نسبتاً گرمی شناسایی شده‌اند. می‌توانید با برنامه‌ریزی مناسب صید کنید.
                <br>صبح زود بهترین زمان است.
        '''
        status_class = "status-good"
        status_text = "شرایط خوب"
    else:
        html_content += '''
                <strong>شرایط متوسط</strong>
                <br>تعداد مناطق گرم محدود است. پیشنهاد می‌شود منتظر روزهای آتی بمانید
                یا مناطق عمیق‌تر را بررسی کنید.
        '''
        status_class = "status-average"
        status_text = "نیاز به احتیاط"
    
    html_content += f'''
            </p>
            <div class="status-badge {status_class}">
                {status_text}
            </div>
        </div>
        
        <div class="main-content">
            <div class="card chart-container">
                <h3><i class="fas fa-chart-bar"></i> نمودار دمایی</h3>
    '''
    
    if chart_file:
        html_content += f'''
                <img src="chart.png" alt="نمودار دمای سطح دریا">
        '''
    else:
        html_content += '''
                <p style="text-align: center; padding: 40px; color: #666;">
                    <i class="fas fa-chart-line fa-3x"></i><br>
                    نمودار در حال تهیه است...
                </p>
        '''
    
    html_content += f'''
            </div>
            
            <div class="card">
                <h3><i class="fas fa-info-circle"></i> اطلاعات تکمیلی</h3>
                <div style="margin-top: 20px;">
                    <p><i class="fas fa-calendar"></i> <strong>تاریخ تحلیل:</strong> {datetime.datetime.now().strftime("%Y/%m/%d")}</p>
                    <p><i class="fas fa-clock"></i> <strong>ساعت به‌روزرسانی:</strong> {datetime.datetime.now().strftime("%H:%M")}</p>
                    <p><i class="fas fa-database"></i> <strong>منبع داده:</strong> NOAA</p>
                    <p><i class="fas fa-map-marker-alt"></i> <strong>منطقه تحت پوشش:</strong> جهانی</p>
                    
                    <div style="margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 10px;">
                        <h4><i class="fas fa-tips"></i> نکات مهم:</h4>
                        <ul style="margin-top: 10px; padding-right: 20px;">
                            <li>بهترین زمان صید: ساعات اولیه صبح</li>
                            <li>دمای ایده‌آل: ۲۲-۲۸ درجه سانتی‌گراد</li>
                            <li>تجهیزات پیشنهادی: قلاب‌های مخصوص ماهی تن</li>
                            <li>همیشه شرایط جوی را بررسی کنید</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        
        <footer>
            <p>این سیستم به صورت خودکار هر روز نتایج را به‌روز می‌کند</p>
            <p>تمامی داده‌ها از مرکز ملی اقیانوسی و جوی (NOAA) دریافت می‌شوند</p>
            <div class="update-time">
                <i class="fas fa-sync-alt"></i> آخرین بروزرسانی: {datetime.datetime.now().strftime("%Y/%m/%d %H:%M")}
            </div>
        </footer>
    </div>
</body>
</html>
    '''
    
    # ذخیره فایل HTML
    with open(website_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("✅ وب‌سایت پیشرفته ایجاد شد: website/index.html")
    
    # ایجاد فایل راهنمای استفاده
    with open(website_dir / "README.txt", "w", encoding="utf-8") as f:
        f.write("""
📋 راهنمای استفاده از وب‌سایت تحلیل ماهی‌گیری

1. فایل index.html را با مرورگر باز کنید
2. نتایج به صورت خودکار هر روز به‌روز می‌شوند
3. می‌توانید این فایل‌ها را روی هاست آپلود کنید

🎯 ویژگی‌ها:
- نمایش دمای سطح دریا
- شناسایی مناطق گرم
- نمودارهای گرافیکی
- توصیه‌های عملیاتی
- طراحی واکنش‌گرا (مخصوص موبایل)

⚠️ نکات:
- داده‌ها از NOAA دریافت می‌شوند
- تحلیل هر روز نیمه‌شب به‌روز می‌شود
- نتایج در پوشه results ذخیره می‌شوند
        """)

if __name__ == "__main__":
    create_advanced_website()
