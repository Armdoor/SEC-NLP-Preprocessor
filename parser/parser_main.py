'''
Basically we will be usinmg this code, parser_main.py, to find all the folders that we stored locally using sec_api and 
use this parser main to find all the company names that we have data on and then run a loop to parse each of the filling
type. then we call the companies.pt to parse the filing type for each company. companies.py uses the functions from 
parser.py to process and store the extracted data into a preprocessed folder under each filing type of the company.
'''
import os
import json
from typing import List, Dict, Tuple
from companies import companies_main
import logging
root_path = "/Volumes/T7/data"
from concurrent.futures import ThreadPoolExecutor
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from load import Loader
from json_data_collector import JsonDataCollector
from datetime import datetime


from dataclasses import dataclass, fields, field
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
    insiderTransactionForOwnerExists: Optional[int] = None
    insiderTransactionForIssuerExists: Optional[int] = None
    name: Optional[str] = None
    tickers: List[str] = None
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
    filings: Dict = field(default_factory=dict)
    # total_num_of_filings: Optional[int] = field(default=0)

    # Computed properties
    @property
    def num_of_former_names(self) -> int:
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
        # self.total_num_of_filings = self.total_num_of_filings or 0




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
        json_collector = JsonDataCollector(root_path, ticker)
        json_data = json_collector.collect_data() # returns a dictionary

        # Insert the json data into the database
        if json_data:
            company_id =process_json_data(json_data, loader)
            print("company_id after return: ", company_id)
        else:
            logging.error(f"Failed to load JSON data for {ticker}")


        # Process files
        for text_file in text_files:
            file_path = os.path.join(raw_folder_path, text_file)
            filing_name = os.path.splitext(text_file)[0]  # Fix multi-dot filenames
            try:
                companies_main(file_path, preprocessed_folder_path, filing_name,filing_type, ticker, loader, company_id)
                logging.info(f"Parsed filing: {filing_name}")
                logging.info("-" * 80)
            except Exception as e:
                logging.error(f"Failed to parse {filing_name}: {str(e)}", exc_info=True)

    except Exception as e:
        logging.error(f"Critical error for {ticker}/{filing_type}: {str(e)}", exc_info=True)

##############################################--PRCEESSING FILES END--##################################################

def process_json_data(json_data, loader):
    entity = EntityData(
                **{k: json_data.get(k) for k in EntityData.__annotations__})
    company_data = (
        entity.cik, 
        entity.entityType, 
        entity.sic,
        entity.sicDescription, 
        entity.ownerOrg, 
        int(entity.insiderTransactionForOwnerExists),
        int(entity.insiderTransactionForIssuerExists), 
        entity.name, 
        ",".join(entity.tickers) if entity.tickers else "", 
        ",".join(entity.exchanges) if entity.exchanges else "",
        entity.ein, 
        entity.description, 
        entity.website, 
        entity.investorWebsite, 
        entity.category, 
        entity.fiscalYearEnd, 
        entity.stateOfIncorporation, 
        entity.stateOfIncorporationDescription, 
        entity.phone,
        entity.total_num_of_filings
        )
            
    # Insert the company data into the database
    try:
        loaded_company_metadata, error, company_id = loader.insert_companies_bulk([company_data])
        print("loaded_company_metadata id : ", company_id)
        if loaded_company_metadata:
            logging.info(f"Successfully inserted company data for {ticker}")
        else:
            logging.error(f"Failed to insert company data for {ticker}: {str(error)} in load")
    except Exception as e:
        logging.error(f"Failed to insert company data for {ticker}: {str(e)} in main")
    # print("Company ID:", company_id)
    company_addresses = entity.addresses
    if company_id is not None:
        if company_addresses:
            parsed_addresses = parse_address_data(company_id, entity.addresses)
            try:
                if parsed_addresses:
                    loaded_company_addresses, error = loader.insert_addresses(parsed_addresses)
                    if loaded_company_addresses:
                        logging.info(f"Successfully inserted company addresses for {ticker}")
                    else:
                        logging.error(f"Failed to insert company addresses for {ticker}: {str(error)} in load")
            except Exception as e:
                logging.error(f"Failed to insert company addresses for {ticker}: {str(e)} in main")
            parsed_former_names = parse_former_names_data(company_id, entity.formerNames)
            try:
                if len(parsed_former_names) > 0:
                    # print("Former Names types: ", type(parsed_former_names), type(parsed_former_names[0]), parsed_former_names)
                    loaded_former_names, error = loader.insert_former_names(parsed_former_names)
                    if loaded_former_names:
                        logging.info(f"Successfully inserted company former names for {ticker}")
                    else:
                        logging.error(f"Failed to insert company former names for {ticker}: {str(error)} in load")
            except Exception as e:
                logging.error(f"Failed to insert company former names for {ticker}: {str(e)} in main")
    print("company_id before return: ", company_id)
    return company_id
    # else:
        # logging.error(f"Failed to insert company data for {ticker}: {str(e)} in main due to missing company ID")
        # return None




##############################################--MAIN--##################################################################
# def main(root_path, company_folder_names, processed_folder_created, filing_types):
#     loader = Loader()
    
#     try:
#         if len(company_folder_names) == 0:
#             company_folder_names = company_folders(root_path)
#         if not processed_folder_created:
#             create_preprocessed_folders(company_folder_names, root_path)
        
#         for filing_type in filing_types:
#             for company_name in company_folder_names:
#                 print(f"Processing {filing_type} filings for {company_name}")
#                 print("-" * 80)
#                 process_text_files(root_path, company_name, filing_type, loader)
#     finally:
#         loader.close()


##############################################--MAIN ENDAS--############################################################


# root_path = "/Volumes/T7/data"
# main(root_path, company_folder_names, processed_folder_created, filing_types)

def print_entity_data(entity):
    # Print dataclass fields
    for field in fields(entity):
        value = getattr(entity, field.name)
        print(f"{field.name}: {value}")
    
    # Print computed properties
    properties = [attr for attr in dir(EntityData) if isinstance(getattr(EntityData, attr, None), property)]
    for prop in properties:
        value = getattr(entity, prop)
        print(f"{prop}: {value}")

def parse_address_data(company_id, addresses):
    """
    Convert the address dictionary into a list of tuples suitable for database insertion.
    :param company_id: ID of the associated company
    :param addresses: Dictionary containing address information
    :return: List of tuples with formatted address data
    """
    parsed_addresses = []
    
    for address_type, details in addresses.items():
        street1 = details.get('street1')
        street2 = details.get('street2')
        city = details.get('city')
        state = details.get('stateOrCountry')
        zip_code = details.get('zipCode')
        country = details.get('stateOrCountryDescription')

        parsed_addresses.append((
            company_id, address_type, street1, street2, city, state, zip_code, country
        ))

    return parsed_addresses


def parse_former_names_data(company_id, former_names):
    parsed_former_names = []
    for former_name in former_names:
        name = former_name.get('name')
        from_date_str = former_name.get('from')
        to_date_str = former_name.get('to')
        
        # Parse 'from' date and time
        from_dt = datetime.strptime(from_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        from_date = from_dt.strftime('%Y-%m-%d')  # Extracts date part
        from_time = from_dt.strftime('%H:%M:%S')  # Extracts time part without milliseconds
        
        # Parse 'to' date and time
        to_dt = datetime.strptime(to_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        to_date = to_dt.strftime('%Y-%m-%d')
        to_time = to_dt.strftime('%H:%M:%S')
        
        # Append separated components to the result
        parsed_former_names.append((
            company_id, name, 
            from_date, from_time, 
            to_date, to_time
        ))
    return parsed_former_names

root_path = '/Users/akshitsanoria/Desktop/PythonP/data1/'
ticker = 'AAPL'
filing_type = '8-KT'
loader = Loader()
id = process_text_files(root_path, ticker, filing_type, loader)
print("company_id: ", id)