'''
Basically we will be usinmg this code, parser_main.py, to find all the folders that we stored locally using sec_api and 
use this parser main to find all the company names that we have data on and then run a loop to parse each of the filling
type. then we call the companies.pt to parse the filing type for each company. companies.py uses the functions from 
parser.py to process and store the extracted data into a preprocessed folder under each filing type of the company.
'''
import os
from companies import companies_main
root_path = "/Volumes/T7/data"


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


def process_text_files(root_path, cmp_name, filing_type):

    # create the path to the raw folder and check if it exists in the directory
    raw_folder_path = os.path.join(root_path,cmp_name, "raw", filing_type)
    if not os.path.exists(raw_folder_path):  
        print(f"Path does not exist: {raw_folder_path}")
        return

   # if raw folder exists, then get all the text files names in the raw folder
    text_files = [
        file for file in os.listdir(raw_folder_path) 
        if file.endswith(".txt") and not file.startswith("._")  # Skip ._ files
    ]

    #now we can create the path to the preprocessed folder and if the filing type folder doesn't exist, create it
    preprocessed_folder_path = os.path.join(root_path, cmp_name, "preprocessed", filing_type)
    os.makedirs(preprocessed_folder_path, exist_ok=True)
    

    # Iterate through the text files in the raw folder to parse the filings
    for text_file in text_files:
        # create the path to the raw file
        file_path = os.path.join(raw_folder_path, text_file)
        # find the filing name
        filing_name = text_file.split(".")[0]
        # calling the main function to parse the filing step by step
        companies_main(file_path, preprocessed_folder_path, filing_name, cmp_name)
        print("-"*80)
        print("Parsed filing ", filing_name)
        print("-"*80)


##############################################--PRCEESSING FILES END--##################################################

##############################################--MAIN--##################################################################
def main(root_path, company_folder_names, processed_folder_created, filing_types):
    # call the one timer functions to get all the company names and create the preprocessed folders
    if len(company_folder_names) == 0:
        company_folder_names = company_folders(root_path)
    if processed_folder_created == False:
        create_preprocessed_folders(company_folder_names, root_path)
    
    # Now we can process the filings
    
    for filing_type in filing_types:
        for comapany_name in company_folder_names:
            print(f"Processing {filing_type} filings for {comapany_name}")
            print("-"*80)
            process_text_files(root_path, comapany_name, filing_type)


##############################################--MAIN ENDAS--############################################################


root_path = "/Volumes/T7/data"
main(root_path, company_folder_names, processed_folder_created, filing_types)