"""
Simple test script for copernicusmarine
"""

import os
import sys

print("=" * 50)
print("STARTING SCRIPT")
print("=" * 50)

# Check if we have credentials
username = os.getenv("COPERNICUS_USERNAME")
password = os.getenv("COPERNICUS_PASSWORD")

if username and password:
    print(f"✅ Found credentials: {username[:3]}***")
else:
    print("❌ No credentials found in environment")
    print("   Make sure COPERNICUS_USERNAME and COPERNICUS_PASSWORD are set")

# Try to import copernicusmarine
try:
    from copernicusmarine import get_credentials
    print("✅ Successfully imported get_credentials")
    
    # Try to use it
    user, pwd = get_credentials()
    print(f"✅ Got credentials using get_credentials(): {user[:3]}***")
    
except Exception as e:
    print(f"❌ Error: {e}")

# Create a simple file
import datetime
try:
    with open("results/test.txt", "w") as f:
        f.write(f"Test successful at {datetime.datetime.now()}\n")
        if username:
            f.write(f"Username: {username[:3]}***\n")
    print("✅ Created results/test.txt")
except:
    print("❌ Could not create results folder")

print("=" * 50)
print("SCRIPT FINISHED")
print("=" * 50)
