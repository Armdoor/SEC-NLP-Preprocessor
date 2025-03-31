'''
Basically we will be usinmg this code, parser_main.py, to find all the folders that we stored locally using sec_api and 
use this parser main to find all the company names that we have data on and then run a loop to parse each of the filling
type. then we call the companies.pt to parse the filing type for each company. companies.py uses the functions from 
parser.py to process and store the extracted data into a preprocessed folder under each filing type of the company.
'''
import os
from typing import List, Dict, Tuple
from .companies import companies_main
import logging
root_path = "/Volumes/T7/data"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
from .json_data_collector import JsonDataCollector
from datetime import datetime
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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

##############################################--ONE TIMER FUNCTIONS--###################################################

# One timer functions to get all the company names and create the preprocessed folders
def company_folders(root_path):
# Get all folder names
    folder_names = [name for name in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, name))]
    
    if type(folder_names) == type(None):                                                                                                         
        logging.warning("No folders found in the path")
        return None                          
    return folder_names


def create_preprocessed_folders(folder_names, root_path):
    if folder_names is None:
        logging.warning("No folders found in the path for creating preprocessed folders")
        return None
    for folder_name in folder_names:
        create_folder_at_path = os.path.join(root_path, folder_name, "preprocessed")
        os.makedirs(create_folder_at_path, exist_ok=True)
        # create_folder_at_path2 = os.path.join(root_path, folder_name, "preprocessed2")
        # os.makedirs(create_folder_at_path2, exist_ok=True)



##############################################--ONE TIMER FUNCTIONS END--###############################################

##############################################--PROCESSING FILES--######################################################

# This function is called by the main function to process the filings for the filing type which then calls the companies.py
# to parse the filing type for each company. companies.py uses the functions from parser.py to process and store the 
# extracted data into a preprocessed folder under each filing type of the company.


def process_text_files(root_path, ticker, filing_type):
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
        # preprocessed_folder_path2 = os.path.join(root_path, ticker, "preprocessed2", filing_type)
        # os.makedirs(preprocessed_folder_path2, exist_ok=True)
        #  extract json metadata
        json_collector = JsonDataCollector(root_path, ticker)
        json_data = json_collector.collect_data() # returns a dictionary
        json_data["filing_type"] = filing_type
        comp_data_list = []
        # Process files
        for text_file in text_files:
            file_path = os.path.join(raw_folder_path, text_file)
            filing_name = os.path.splitext(text_file)[0]  # Fix multi-dot filenames
            try:
                company_data = companies_main(file_path, preprocessed_folder_path ,filing_name,filing_type, ticker)
                logging.info(f"Parsed filing: {filing_name}")
                print("-" * 80)
                fin_comp_data = {
                    'company_data': company_data['in_filing_data'],
                    'json_data': json_data,
                    'metadata': company_data
                }
                comp_data_list.append(fin_comp_data)
                return comp_data_list 
            except Exception as e:
                logging.error(f"Failed to parse {filing_name}: {str(e)} in parser_main.py", exc_info=True)
    except Exception as e:
        logging.error(f"Critical error for {ticker}/{filing_type}: {str(e)} in parser_main.py", exc_info=True)
        return []

##############################################--PRCEESSING FILES END--##################################################


def process_json_data(json_data):
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
    return company_data
   




##############################################--MAIN--##################################################################
def main(root_path, company_folder_names, processed_folder_created, filing_types):

    companies_stored =[]
    all_comp_data = []  # List to collect all processed data
    try:
        if len(company_folder_names) == 0:
            company_folder_names = company_folders(root_path)
        if not processed_folder_created:
            create_preprocessed_folders(company_folder_names, root_path)
        
        for filing_type in filing_types:
            for company_name in company_folder_names:
                print(f"Processing {filing_type} filings for {company_name}")
                print("-" * 80)
                comp_data = process_text_files(root_path, company_name, filing_type)
                companies_stored.append((company_name, filing_type))
                all_comp_data.append(comp_data)
    except Exception as e:
        logging.error(f"Error processing companies: {str(e)}", exc_info=True)
    return all_comp_data , filing_type
    


##############################################--MAIN ENDAS--############################################################





def parse_address_data(addresses):
    """
    Convert the address dictionary into a list of tuples suitable for database insertion.
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
            address_type, street1, street2, city, state, zip_code, country
        ))

    return parsed_addresses


def parse_former_names_data(former_names):
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
            name, 
            from_date, from_time, 
            to_date, to_time
        ))
    return parsed_former_names



# if __name__ == "__main__":
#     root_path = '/Users/akshitsanoria/Desktop/PythonP/testing'
#     company_folder_names = []  # Initialize with an empty list or provide specific company names
#     processed_folder_created = False
#     filing_types = ['8-K', '10-K']

#     all_data = main(root_path, company_folder_names, processed_folder_created, filing_types)
#     print(all_data)


# # root_path = "/Volumes/T7/data"
#     main(root_path, company_folder_names, processed_folder_created, filing_types)
