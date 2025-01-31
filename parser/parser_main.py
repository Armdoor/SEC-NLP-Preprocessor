'''
Basically we will be usinmg this code, parser_main.py, to find all the folders that we stored locally using sec_api and 
use this parser main to find all the company names that we have data on and then run a loop to parse each of the filling
type. then we call the companies.pt to parse the filing type for each company. companies.py uses the functions from 
parser.py to process and store the extracted data into a preprocessed folder under each filing type of the company.
'''
import os
from companies import companies_main
import logging
root_path = "/Volumes/T7/data"
from concurrent.futures import ThreadPoolExecutor
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from ETL import Loader
from parser import JsonDataCollector


from dataclasses import dataclass
from typing import Optional, List, Dict
###############################################--DATA CLASS--####################################################


@dataclass
class EntityData:
    # Primary fields from JSON
    cik: Optional[str] = None
    entityType: Optional[str] = None
    sic: Optional[str] = None
    sicDescription: Optional[str] = None
    ownerOrg: Optional[str] = None
    insiderTransactionForOwnerExists: Optional[bool] = None
    insiderTransactionForIssuerExists: Optional[bool] = None
    name: Optional[str] = None
    exchanges: List[str] = None
    ein: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    investorWebsite: Optional[str] = None
    category: Optional[str] = None
    fiscalYearEnd: Optional[str] = None
    stateOfIncorporation: Optional[str] = None
    stateOfIncorporationDescription: Optional[str] = None
    addresses: Dict = None
    phone: Optional[str] = None
    formerNames: List[str] = None
    filings: Dict = None

    # Computed properties
    @property
    def num_of_form(self) -> int:
        return len(self.formerNames) if self.formerNames else 0

    @property
    def total_num_of_filings(self) -> int:
        try:
            return len(self.filings['recent']['accessionNumber'])
        except (KeyError, TypeError):
            return 0

    def __post_init__(self):
        # Initialize mutable defaults
        self.exchanges = self.exchanges or []
        self.addresses = self.addresses or {}
        self.formerNames = self.formerNames or []
        self.filings = self.filings or {}




##############################################--VARIABLE DECLARATIONS--#################################################

company_folder_names = []
# filing_types = ["8-K", "10-K", "10-Q", "13-D", "DEF 14A", "S-1"]
processed_folder_created = False
filing_types = ['8-K', '10-K']
COMMON_DATA = [
    'cik', 'entityType', 'sic', 'sicDescription',
    'ownerOrg', 'name', 'exchanges', 'ein', 'description',
    'website', 'investorWebsite', 'category', 'fiscalYearEnd',
    'stateOfIncorporation', 'stateOfIncorporationDescription',
    'addresses', 'phone', 'formerNames'
]
##############################################--ONE TIMER FUNCTIONS--###################################################

# One timer functions to get all the company names and create the preprocessed folders
def company_folders(root_path):
# Get all folder names
    folder_names = [name for name in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, name))]
    if type(folder_names) == type(None):                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
        print("No folders found in the path")
        return None                          
    return folder_names

def create_preprocessed_folders(folder_names, root_path):
    if folder_names is None:
        print("No folders found in the path for creating preprocessed folders")
        return None
    for folder_name in folder_names:
        create_folder_at_path = os.path.join(root_path, folder_name, "preprocessed")
        os.makedirs(create_folder_at_path, exist_ok=True)
    processed_folder_created = True


##############################################--ONE TIMER FUNCTIONS END--###############################################

##############################################--PROCESSING FILES--######################################################

# This function is called by the main function to process the filings for the filing type which then calls the companies.py
# to parse the filing type for each company. companies.py uses the functions from parser.py to process and store the 
# extracted data into a preprocessed folder under each filing type of the company.


def process_text_files(root_path, ticker, filing_type, loader):
    raw_folder_path = os.path.join(root_path, ticker, "raw", filing_type)
    try:
        if not os.path.exists(raw_folder_path):
            logging.warning(f"Path does not exist: {raw_folder_path} (Company: {ticker}, Filing: {filing_type})")
            return

        # Get text files (handle race conditions)
        try:
            text_files = [
                file for file in os.listdir(raw_folder_path)
                if file.endswith(".txt") and not file.startswith("._")
            ]
        except FileNotFoundError:
            logging.warning(f"Folder deleted after check: {raw_folder_path}")
            return

        # Create preprocessed folder
        preprocessed_folder_path = os.path.join(root_path, ticker, "preprocessed", filing_type)
        os.makedirs(preprocessed_folder_path, exist_ok=True)

        #  extract json metadata
        json_collector = JsonDataCollector(raw_folder_path, ticker)
        json_data = json_collector.collect_data() # returns a dictionary

        # Insert the json data into the database
        if json_data:
            entity = EntityData(
                **{k: json_data.get(k) for k in EntityData.__annotations__})
            
            company_data = (
                entity.cik, 
                entity.entity_type, 
                entity.name, 
                entity.ticker, 
                entity.industry,
                entity.sic, 
                entity.sic_description, 
                entity.owner_org, 
                int(entity.insider_transaction_for_owner_exists),
                int(entity.insider_transaction_for_issuer_exists), 
                entity.ein, 
                entity.description, 
                entity.website, 
                entity.investor_website, 
                entity.category, 
                entity.fiscal_year_end, 
                entity.state_of_incorporation, 
                entity.state_of_incorporation_description, 
                entity.phone
            ) 
            try:
                data_helper(loader, company_data)
                logging.info(f"Successfully inserted company data for {ticker}")
            except Exception as e:
                logging.error(f"Failed to insert company data for {ticker}: {str(e)}")
        # Process files
        for text_file in text_files:
            file_path = os.path.join(raw_folder_path, text_file)
            filing_name = os.path.splitext(text_file)[0]  # Fix multi-dot filenames
            try:
                companies_main(file_path, preprocessed_folder_path, filing_name, ticker, loader, company_id, entity)
                logging.info(f"Parsed filing: {filing_name}")
                logging.info("-" * 80)
            except Exception as e:
                logging.error(f"Failed to parse {filing_name}: {str(e)}", exc_info=True)

    except Exception as e:
        logging.error(f"Critical error for {ticker}/{filing_type}: {str(e)}", exc_info=True)

##############################################--PRCEESSING FILES END--##################################################

##############################################--MAIN--##################################################################
def main(root_path, company_folder_names, processed_folder_created, filing_types):
    loader = Loader()
    
    try:
        if len(company_folder_names) == 0:
            company_folder_names = company_folders(root_path)
        if not processed_folder_created:
            create_preprocessed_folders(company_folder_names, root_path)
        
        for filing_type in filing_types:
            for company_name in company_folder_names:
                print(f"Processing {filing_type} filings for {company_name}")
                print("-" * 80)
                process_text_files(root_path, company_name, filing_type, loader)
    finally:
        loader.close()


##############################################--MAIN ENDAS--############################################################


root_path = "/Volumes/T7/data"
# main(root_path, company_folder_names, processed_folder_created, filing_types)

