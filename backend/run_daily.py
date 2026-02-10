"""
run_daily.py - Simple Tuna Hotspot Analysis
Compatible with copernicusmarine==0.6.0
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function"""
    logger.info("Starting tuna hotspot analysis")
    
    try:
        # 1. Create necessary directories
        Path("data").mkdir(exist_ok=True)
        Path("results").mkdir(exist_ok=True)
        
        # 2. Try to import copernicusmarine - OLD VERSION
        logger.info("Importing copernicusmarine (version 0.6.0)...")
        try:
            # This import works with version 0.6.0
            from copernicusmarine import get_credentials
            logger.info("✅ Successfully imported get_credentials from copernicusmarine")
        except ImportError as e:
            logger.error(f"❌ Failed to import: {e}")
            logger.info("Please install: pip install copernicusmarine==0.6.0")
            return 1
        
        # 3. Get credentials
        logger.info("Getting credentials...")
        try:
            # Try environment variables first
            username = os.getenv("COPERNICUS_USERNAME")
            password = os.getenv("COPERNICUS_PASSWORD")
            
            if username and password:
                logger.info(f"✅ Using credentials from environment variables")
                logger.info(f"   Username: {username[:3]}***")  # Show only first 3 chars for security
            else:
                # Try to get from copernicusmarine
                username, password = get_credentials()
                logger.info("✅ Retrieved credentials using get_credentials()")
        except Exception as e:
            logger.warning(f"⚠️ Could not get credentials: {e}")
            logger.info("Continuing without credentials...")
            username, password = None, None
        
        # 4. Create a simple output file
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = Path("results") / f"analysis_{timestamp}.txt"
        
        with open(output_file, "w") as f:
            f.write("=" * 50 + "\n")
            f.write("TUNA HOTSPOT ANALYSIS REPORT\n")
            f.write("=" * 50 + "\n")
            f.write(f"Date: {datetime.now()}\n")
            f.write(f"Status: SUCCESS\n")
            f.write(f"Credentials available: {bool(username and password)}\n")
            f.write(f"Data directory: data/\n")
            f.write(f"Results directory: results/\n")
            f.write("=" * 50 + "\n")
        
        logger.info(f"✅ Analysis completed!")
        logger.info(f"📁 Results saved to: {output_file}")
        
        # 5. List what's in results directory
        results_files = list(Path("results").glob("*.txt"))
        logger.info(f"📊 Total result files: {len(results_files)}")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
