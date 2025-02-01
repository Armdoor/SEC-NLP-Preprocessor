import os
import json
import logging
from glob import glob
import fnmatch
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
            find_path = os.path.join(self.path, self.ticker)
            join_path = [f for f in os.listdir(find_path) if fnmatch.fnmatch(f, '*.json')]
            json_path = os.path.join(self.path, self.ticker, join_path[0])
            if not json_path:
                logger.warning(f"No JSON files found for {self.ticker} for path {json_path} in json_data_collector.py")
                return {}

            json_d = json_path
            try:
                with open(json_d, 'r') as f:
                    self.json_data = json.load(f)
                logger.info(f"Successfully loaded JSON data for {self.ticker} in json_data_collector.py")
            except Exception as e:
                logger.error(f"Failed to load JSON data for {self.ticker}: {str(e)} in json_data_collector.py")
                return {}

            return self.json_data
