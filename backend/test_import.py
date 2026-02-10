import sys
print("Python version:", sys.version)

# Try different import methods
try:
    from copernicusmarine import get_credentials
    print("✅ Method 1: from copernicusmarine import get_credentials - SUCCESS")
except ImportError as e:
    print("❌ Method 1 failed:", e)

try:
    from copernicusmarine import CopernicusMarine
    print("✅ Method 2: from copernicusmarine import CopernicusMarine - SUCCESS")
except ImportError as e:
    print("❌ Method 2 failed:", e)

try:
    import copernicusmarine
    print("✅ Method 3: import copernicusmarine - SUCCESS")
    print("   Available functions:", [x for x in dir(copernicusmarine) if not x.startswith('_')])
except ImportError as e:
    print("❌ Method 3 failed:", e)
