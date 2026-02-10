"""
ایجاد یک صفحه وب ساده برای نمایش نتایج
"""

from pathlib import Path
import json
import datetime

def create_website():
    """ایجاد فایل HTML برای نمایش نتایج"""
    
    # پیدا کردن آخرین نتایج
    results_dir = Path("results")
    json_files = list(results_dir.glob("*.json"))
    
    if not json_files:
        return
    
    latest_json = sorted(json_files)[-1]
    
    with open(latest_json, 'r') as f:
        data = json.load(f)
    
    # ایجاد HTML
    html_content = f'''
    <!DOCTYPE html>
    <html dir="rtl" lang="fa">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>تحلیل مناطق ماهی‌گیری ماهی تن</title>
        <style>
            body {{
                font-family: Tahoma, sans-serif;
                line-height: 1.8;
                margin: 0;
                padding: 20px;
                background-color: #f0f8ff;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #0066cc;
                text-align: center;
                border-bottom: 3px solid #0066cc;
                padding-bottom: 10px;
            }}
            .stats {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 20px;
                margin: 30px 0;
            }}
            .stat-box {{
                background: #e6f2ff;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                border: 2px solid #0066cc;
            }}
            .stat-value {{
                font-size: 24px;
                font-weight: bold;
                color: #0066cc;
                margin: 10px 0;
            }}
            .recommendation {{
                background: #fff3cd;
                border: 2px solid #ffc107;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
            }}
            .timestamp {{
                text-align: center;
                color: #666;
                font-size: 14px;
                margin-top: 30px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🐟 تحلیل مناطق ماهی‌گیری ماهی تن</h1>
            
            <div class="timestamp">
                آخرین بروزرسانی: {datetime.datetime.now().strftime("%Y/%m/%d %H:%M")}
            </div>
            
            <div class="stats">
                <div class="stat-box">
                    <div>میانگین دما</div>
                    <div class="stat-value">{data.get('mean_temp', 0):.1f}°C</div>
                </div>
                
                <div class="stat-box">
                    <div>مناطق گرم</div>
                    <div class="stat-value">{data.get('hotspot_count', 0):,}</div>
                    <div>نقطه</div>
                </div>
                
                <div class="stat-box">
                    <div>حداکثر دما</div>
                    <div class="stat-value">{data.get('max_temp', 0):.1f}°C</div>
                </div>
                
                <div class="stat-box">
                    <div>درصد مناطق گرم</div>
                    <div class="stat-value">{data.get('hotspot_percentage', 0):.1f}%</div>
                </div>
            </div>
            
            <div class="recommendation">
                <h3>🎯 توصیه امروز:</h3>
                <p>
    '''
    
    # اضافه کردن توصیه بر اساس درصد
    if data.get('hotspot_percentage', 0) > 20:
        html_content += "✅ شرایط عالی برای ماهی‌گیری! مناطق گرم زیادی شناسایی شده‌اند."
    elif data.get('hotspot_percentage', 0) > 10:
        html_content += "🟡 شرایط نسبتاً خوب. می‌توانید برای ماهی‌گیری برنامه‌ریزی کنید."
    else:
        html_content += "🔴 شرایط متوسط. پیشنهاد می‌شود منتظر روزهای آتی بمانید."
    
    html_content += '''
                </p>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <p>این گزارش به صورت خودکار تولید شده است.</p>
                <p>داده‌ها از مرکز ملی اقیانوسی و جوی (NOAA) دریافت می‌شوند.</p>
            </div>
        </div>
    </body>
    </html>
    '''
    
    # ذخیره فایل HTML
    website_dir = Path("website")
    website_dir.mkdir(exist_ok=True)
    
    with open(website_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("🌐 صفحه وب ایجاد شد: website/index.html")

if __name__ == "__main__":
    create_website()
