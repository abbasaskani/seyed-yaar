"""
دانلود داده‌های واقعی دمای سطح دریا
"""

import os
import requests
import logging
from datetime import datetime, timedelta
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def download_copernicus_data():
    """دانلود داده از Copernicus Marine"""
    
    username = os.getenv("COPERNICUS_USERNAME")
    password = os.getenv("COPERNICUS_PASSWORD")
    
    if not username or not password:
        logger.error("Credentials not found")
        return False
    
    logger.info(f"Using username: {username[:3]}***")
    
    # یک فایل نمونه کوچک برای تست
    # این فایل دمای سطح دریا برای یک منطقه کوچکه
    url = "https://my.cmems-du.eu/thredds/fileServer/cmems_mod_glo_phy_my_0.083deg_P1D-m/2024/01/cmems_mod_glo_phy_my_0.083deg_P1D-m_20240101_R20240101.nc"
    
    try:
        logger.info(f"Downloading from: {url}")
        
        # ایجاد پوشه برای داده‌ها
        data_dir = Path("data") / "copernicus"
        data_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = data_dir / "sample_sst.nc"
        
        # دانلود فایل
        response = requests.get(
            url,
            auth=(username, password),
            stream=True,
            timeout=60
        )
        
        if response.status_code == 200:
            # دانلود با قطعات کوچک
            total_size = 0
            with open(output_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        total_size += len(chunk)
            
            # تبدیل به مگابایت
            size_mb = total_size / (1024 * 1024)
            
            logger.info(f"✅ Download successful!")
            logger.info(f"   File: {output_file}")
            logger.info(f"   Size: {size_mb:.2f} MB")
            
            # اطلاعات بیشتر
            if output_file.exists():
                file_stats = output_file.stat()
                logger.info(f"   Created: {datetime.fromtimestamp(file_stats.st_ctime)}")
            
            return True
            
        else:
            logger.error(f"❌ Download failed: HTTP {response.status_code}")
            logger.error(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        return False

def main():
    """تابع اصلی"""
    print("=" * 60)
    print("Copernicus Marine Data Downloader")
    print("=" * 60)
    
    success = download_copernicus_data()
    
    if success:
        print("\n✅ Data download completed successfully!")
        print("   Next steps:")
        print("   1. Check the 'data/copernicus/' folder")
        print("   2. Process the NetCDF files")
        print("   3. Analyze sea surface temperature")
    else:
        print("\n❌ Data download failed")
        print("   Check your credentials and internet connection")
    
    print("=" * 60)
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
