"""
run_daily.py - Tuna Hotspot Analysis Script
Compatible with copernicusmarine >= 0.8.0
"""

import os
import sys
import logging
from datetime import datetime, timedelta
import xarray as xr
import numpy as np
import pandas as pd
from pathlib import Path

# Import copernicusmarine with new API
try:
    from copernicusmarine import CopernicusMarine
    HAS_CM = True
except ImportError as e:
    print(f"Error importing copernicusmarine: {e}")
    print("Please install: pip install copernicusmarine")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TunaHotspotAnalysis:
    def __init__(self):
        """Initialize the analysis class"""
        self.data_dir = Path("data")
        self.output_dir = Path("results")
        self.setup_directories()
        
        # Initialize Copernicus Marine client
        self.cm = CopernicusMarine()
        
    def setup_directories(self):
        """Create necessary directories"""
        self.data_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        (self.output_dir / "maps").mkdir(exist_ok=True)
        (self.output_dir / "stats").mkdir(exist_ok=True)
        
    def get_credentials(self):
        """Get Copernicus Marine credentials"""
        try:
            # Method 1: Using environment variables
            username = os.getenv("COPERNICUS_USERNAME")
            password = os.getenv("COPERNICUS_PASSWORD")
            
            if username and password:
                return username, password
            
            # Method 2: Using the new API
            credentials = self.cm.get_credentials()
            
            # Handle different return formats
            if isinstance(credentials, tuple) and len(credentials) == 2:
                return credentials
            elif isinstance(credentials, dict):
                return credentials.get("username"), credentials.get("password")
            else:
                raise ValueError("Unexpected credentials format")
                
        except Exception as e:
            logger.error(f"Failed to get credentials: {e}")
            raise
    
    def download_data(self, dataset_id, variables, area, date):
        """Download data from Copernicus Marine"""
        try:
            logger.info(f"Downloading data for {date}")
            
            # Format date for query
            date_str = date.strftime("%Y-%m-%d")
            
            # Download data using new API
            dataset = self.cm.subset(
                dataset_id=dataset_id,
                variables=variables,
                minimum_longitude=area[0],
                maximum_longitude=area[1],
                minimum_latitude=area[2],
                maximum_latitude=area[3],
                start_datetime=date_str + "T00:00:00",
                end_datetime=date_str + "T23:59:59",
                output_filename=self.data_dir / f"data_{date_str}.nc",
                overwrite=True
            )
            
            logger.info(f"Data downloaded successfully: {dataset}")
            return dataset
            
        except Exception as e:
            logger.error(f"Failed to download data: {e}")
            return None
    
    def process_data(self, data_file):
        """Process the downloaded data"""
        try:
            logger.info(f"Processing {data_file}")
            
            # Open the dataset
            ds = xr.open_dataset(data_file)
            
            # Example processing: calculate SST anomaly
            if 'thetao' in ds:  # Sea surface temperature
                sst = ds['thetao'].isel(depth=0)  # Surface layer
                
                # Calculate daily mean
                sst_mean = sst.mean(dim=['latitude', 'longitude'], skipna=True)
                
                # Calculate anomaly (simple example)
                climatology = 20.0  # Example climatology value
                anomaly = sst_mean - climatology
                
                return {
                    'sst': sst,
                    'sst_mean': float(sst_mean.values),
                    'anomaly': float(anomaly.values),
                    'timestamp': pd.Timestamp.now()
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to process data: {e}")
            return None
    
    def identify_hotspots(self, processed_data, threshold=0.5):
        """Identify tuna hotspots based on conditions"""
        try:
            if not processed_data or 'sst' not in processed_data:
                return None
            
            sst = processed_data['sst']
            
            # Simple hotspot identification
            # In reality, you'd use more complex criteria
            hotspots = sst.where(sst > sst.mean() + threshold * sst.std())
            
            # Count hotspots
            hotspot_count = np.count_nonzero(~np.isnan(hotspots.values))
            
            return {
                'hotspots': hotspots,
                'count': hotspot_count,
                'threshold': threshold
            }
            
        except Exception as e:
            logger.error(f"Failed to identify hotspots: {e}")
            return None
    
    def save_results(self, results, date):
        """Save analysis results"""
        try:
            date_str = date.strftime("%Y-%m-%d")
            
            # Save to CSV
            results_df = pd.DataFrame([{
                'date': date_str,
                'sst_mean': results.get('sst_mean', np.nan),
                'anomaly': results.get('anomaly', np.nan),
                'hotspot_count': results.get('hotspot_count', 0),
                'processing_time': pd.Timestamp.now()
            }])
            
            csv_path = self.output_dir / f"results_{date_str}.csv"
            results_df.to_csv(csv_path, index=False)
            
            # Save hotspot data as NetCDF
            if 'hotspots' in results:
                hotspot_ds = xr.Dataset({
                    'hotspots': results['hotspots']
                })
                nc_path = self.output_dir / "maps" / f"hotspots_{date_str}.nc"
                hotspot_ds.to_netcdf(nc_path)
            
            logger.info(f"Results saved for {date_str}")
            
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
    
    def run_daily_analysis(self):
        """Main function to run daily analysis"""
        logger.info("Starting daily tuna hotspot analysis")
        
        # Get yesterday's date
        yesterday = datetime.now() - timedelta(days=1)
        
        # Define parameters (adjust based on your needs)
        dataset_id = "cmems_mod_glo_phy_my_0.083deg_P1D-m"  # Example dataset
        variables = ["thetao"]  # Sea water temperature
        area = [-180, 180, -90, 90]  # Global [min_lon, max_lon, min_lat, max_lat]
        
        try:
            # Step 1: Get credentials (optional, depends on dataset)
            username, password = self.get_credentials()
            logger.info("Credentials retrieved successfully")
            
            # Step 2: Download data
            data_file = self.download_data(dataset_id, variables, area, yesterday)
            
            if not data_file:
                logger.error("No data downloaded")
                return False
            
            # Step 3: Process data
            processed_data = self.process_data(data_file)
            
            if not processed_data:
                logger.error("Failed to process data")
                return False
            
            # Step 4: Identify hotspots
            hotspots = self.identify_hotspots(processed_data)
            
            if hotspots:
                processed_data['hotspots'] = hotspots['hotspots']
                processed_data['hotspot_count'] = hotspots['count']
            
            # Step 5: Save results
            self.save_results(processed_data, yesterday)
            
            logger.info("Daily analysis completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return False

def main():
    """Main entry point"""
    try:
        # Initialize and run analysis
        analysis = TunaHotspotAnalysis()
        success = analysis.run_daily_analysis()
        
        if success:
            logger.info("Script completed successfully")
            sys.exit(0)
        else:
            logger.error("Script failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Script interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
