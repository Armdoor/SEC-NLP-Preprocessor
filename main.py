"""
A top-level script to run the entire pipeline.
"""

import json  # Import the JSON module for potential JSON operations.
import logging  # Import logging for tracking progress and errors.

# Import the main parsing function from the sec_parser package (aliased to parse_main).
from sec_parser.parser_main import main as parse_main

# Import the data cleaning function from the Cleaner package (aliased to clean_main).
from Cleaner.main import clean_data as clean_main

# Import all models defined in the Cleaner.models module.
from Cleaner.models import *

# Import the Importer class which handles database insertions from Cleaner.insert_data.
from Cleaner.insert_data import Importer


def main():
    # Define the root path where the files to be processed are stored.
    root_path = '/Users/akshitsanoria/Desktop/PythonP/Testing_Folder'
    
    # Initialize an empty list for company folder names (for possible use in filtering specific folders).
    company_folder_names = []
    
    # Flag to indicate whether a processed folder has been created (affects file handling).
    processed_folder_created = False
    
    # Define the list of filing types to process; currently set to only '8-K' filings.
    filing_types = ['8-K']
    
    # ---------------------------------------------------------------
    # STEP 1: Parse the files.
    # ---------------------------------------------------------------
    # Call the parsing function with the given parameters:
    # - root_path: Directory containing files.
    # - company_folder_names: (Optional) Specific folder names to process.
    # - processed_folder_created: Whether a folder for processed files already exists.
    # - filing_types: Which filing types to parse.
    # The function returns a tuple containing:
    #   - all_data: The parsed data from all files.
    #   - filing_type: The type of filing processed.
    all_data, filing_type = parse_main(root_path, company_folder_names, processed_folder_created, filing_types)
    
    # Define a path to store a textual record of the parsed data (useful for debugging or record keeping).
    p = "/Users/akshitsanoria/Desktop/PythonP/printing_files/8ktesting/parsed.txt"
    
    # Open the specified file in write mode with UTF-8 encoding.
    with open(p, 'w', encoding='utf-8') as file:
        # Write the string representation of the parsed data to the file.
        file.write(str(all_data))
    
    # Log that the parsing phase has been successfully completed.
    logging.info("Parsing completed.")
    
    # ---------------------------------------------------------------
    # STEP 2: Prepare and insert data into the database.
    # ---------------------------------------------------------------
    # Define a company name to use when inserting data into the database.
    company_name = "APPL"
    
    # Create an instance of the Importer class to handle database operations.
    impo = Importer()
    
    # Call the method to create all required database tables if they don't exist.
    impo.create_tables()

    # ---------------------------------------------------------------
    # STEP 3: Process and insert each filing from the parsed data.
    # ---------------------------------------------------------------
    # Loop over each filing in the parsed data.
    for i, filing in enumerate(all_data):
        try:
            # Log the progress of filing processing (shows the current filing number).
            logging.info(f"Processing filing {i + 1}/{len(all_data)}...")
            
            # Iterate over each element in the current filing.
            for j in filing:
                # Extract company-specific data from the filing's metadata.
                comp_data = j["metadata"]["in_filing_data"]
                
                # Retrieve the unique accession number for the filing.
                accession_number = j['accession_number']
                
                # Clean the extracted data using the cleaning function.
                # The clean_main function returns a report object (likely of type Report8K).
                report = clean_main(comp_data, filing_type, accession_number)
                
                # Print the accession number for real-time feedback/debugging.
                print("accession_number: ", accession_number)
                
                # If the cleaned report is of type Report8K, then process this report.
                if type(report) == Report8K:
                    # Call the process_report8k method of the Importer to insert the report into the database.
                    impo.process_report8k(company_name, report, accession_number)
        except Exception as e:
            # In case of any errors during the filing processing, log the error.
            logging.error(f"Error processing filing {i + 1}: {e}")
            # Continue processing subsequent filings even if one fails.
            continue  
    # Log that all filings have been processed.
    logging.info("Processing completed.")


# If the script is being run directly (and not imported as a module), execute the main function.
if __name__ == "__main__":
    main()
