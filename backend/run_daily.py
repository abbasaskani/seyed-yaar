#!/usr/bin/env python3
"""
اسکریپت اصلی صیدیار - با اتصال واقعی به Copernicus Marine
"""

import os
import json
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import xarray as xr

try:
    from copernicusmarine import subset, get_credentials
    print("✅ Copernicus Marine library loaded successfully")
except ImportError as e:
    print(f"❌ Error importing copernicusmarine: {e}")
    print("Please install: pip install copernicusmarine")
    exit(1)

# تنظیمات
BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "docs" / "latest"
CONFIG_DIR = BASE_DIR / "backend" / "config"

# منطقه دریای عربی (مختصات شما)
ARABIAN
