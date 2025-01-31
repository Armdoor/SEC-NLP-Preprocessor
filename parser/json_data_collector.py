import os
import json
import logging
from glob import glob

# Configure the logger
logging.basicConfig(level=logging.INFO, 
                            format='%(asctime)s - %(levelname)s - %(message)s', 
                            handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

class JsonDataCollector:
    def __init__(self, path, ticker):
        self.path = path
        self.ticker = ticker
        self.json_data = {}


    def collect_data(self):
            json_path = glob(os.path.join(self.path, self.ticker, "*.json"))
            
            if not json_path:
                logger.warning(f"No JSON files found for {self.ticker}")
                return {}

            json_d = json_path[0]
            try:
                with open(json_d, 'r') as f:
                    self.json_data = json.load(f)
                logger.info(f"Successfully loaded JSON data for {self.ticker}")
            except Exception as e:
                logger.error(f"Failed to load JSON data for {self.ticker}: {str(e)}")
                return {}

            # Remove 'filings' key if it exists
            self.remove_filings()
            return self.json_data

    def remove_filings(self):
            if 'filings' in self.json_data:
                del self.json_data['filings']
                logger.info(f"Removed 'filings' key from the data for {self.ticker}.")