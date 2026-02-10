"""
پردازش داده‌های دمای سطح دریا
"""

import xarray as xr
import numpy as np
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_sst_data(file_path):
    """آنالیز داده‌های SST"""
    
    logger.info(f"📂 باز کردن فایل: {file_path}")
    
    try:
        # باز کردن فایل NetCDF
        ds = xr.open_dataset(file_path)
        
        logger.info("✅ فایل NetCDF با موفقیت باز شد")
        
        # نمایش اطلاعات
        print("\n" + "="*50)
        print("مشخصات داده‌ها:")
        print("="*50)
        
        print(f"📊 ابعاد داده: {dict(ds.dims)}")
        print(f"🔤 متغیرها: {list(ds.variables.keys())}")
        
        # اگر دمای سطح دریا وجود دارد
        if 'thetao' in ds:
            sst = ds['thetao']
            
            print(f"\n🌡️ دمای سطح دریا (SST):")
            print(f"   شکل: {sst.shape}")
            print(f"   واحد: {sst.units if 'units' in sst.attrs else 'نامشخص'}")
            
            # محاسبات ساده
            sst_values = sst.values
            mask = ~np.isnan(sst_values)
            
            if np.any(mask):
                valid_values = sst_values[mask]
                print(f"   حداقل: {np.nanmin(valid_values):.2f}°C")
                print(f"   حداکثر: {np.nanmax(valid_values):.2f}°C")
                print(f"   میانگین: {np.nanmean(valid_values):.2f}°C")
                
                # ذخیره نتایج
                results = {
                    'file': str(file_path),
                    'min_temp': float(np.nanmin(valid_values)),
                    'max_temp': float(np.nanmax(valid_values)),
                    'mean_temp': float(np.nanmean(valid_values)),
                    'shape': sst.shape
                }
                
                return results
        
        return None
        
    except Exception as e:
        logger.error(f"❌ خطا در پردازش: {e}")
        return None

if __name__ == "__main__":
    # جستجوی فایل‌های NetCDF
    data_dir = Path("data/copernicus")
    
    if data_dir.exists():
        nc_files = list(data_dir.glob("*.nc"))
        
        if nc_files:
            print(f"🔍 یافت شد {len(nc_files)} فایل NetCDF")
            
            for file in nc_files:
                print(f"\n📄 پردازش: {file.name}")
                results = analyze_sst_data(file)
                
                if results:
                    # ذخیره نتایج در فایل
                    import json
                    import datetime
                    
                    output_file = Path("results") / f"sst_analysis_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    
                    with open(output_file, 'w') as f:
                        json.dump(results, f, indent=2)
                    
                    print(f"💾 نتایج ذخیره شد در: {output_file}")
        else:
            print("❌ هیچ فایل NetCDF یافت نشد")
            print("   ابتدا فایل‌ها را دانلود کنید")
    else:
        print("❌ پوشه data/copernicus وجود ندارد")
