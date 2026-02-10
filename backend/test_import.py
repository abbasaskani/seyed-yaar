import sys
print("=" * 50)
print("Python version:", sys.version)
print("=" * 50)

# Try different import methods
print("\n1. Trying: from copernicusmarine import get_credentials")
try:
    from copernicusmarine import get_credentials
    print("✅ SUCCESS - get_credentials imported")
    print("   Function:", get_credentials)
except ImportError as e:
    print("❌ FAILED:", e)

print("\n2. Trying: from copernicusmarine import CopernicusMarine")
try:
    from copernicusmarine import CopernicusMarine
    print("✅ SUCCESS - CopernicusMarine imported")
    print("   Class:", CopernicusMarine)
except ImportError as e:
    print("❌ FAILED:", e)

print("\n3. Trying: import copernicusmarine")
try:
    import copernicusmarine
    print("✅ SUCCESS - module imported")
    print("   Available functions:", [x for x in dir(copernicusmarine) if not x.startswith('_')])
except ImportError as e:
    print("❌ FAILED:", e)

print("\n" + "=" * 50)
print("Test completed!")
print("=" * 50)
