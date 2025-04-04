"""
A top-level script to run the entire pipeline.

"""
import json
import logging 
from sec_parser.parser_main import main as parse_main
from Cleaner.main import clean_data as clean_main
from Cleaner.models import *
from Cleaner.insert_data import Importer


def main():
    root_path = '/Users/akshitsanoria/Desktop/PythonP/Testing_Folder'
    company_folder_names = []
    processed_folder_created = False
    filing_types = ['8-K']
    
    # Step 1: Parse the files
    all_data, filing_type = parse_main(root_path, company_folder_names, processed_folder_created, filing_types)
    
    logging.info("Parsing completed.")
    
    impo = Importer()
    impo.create_tables()

    # Process each filing
    for i, filing in enumerate(all_data):
        try:
            logging.info(f"Processing filing {i + 1}/{len(all_data)}...")
            for j in filing:
                comp_data = j["metadata"]["in_filing_data"]
                accession_number = j['accession_number']
                cleaned_data = clean_main(comp_data, filing_type, accession_number)
                print("accession_number: ",accession_number)
                for k, v in cleaned_data.sections.items():
                    print("v  ", v, "  k  ", k)
                    for curr_sec in v.items:
                        curr_item = v.get_item(curr_sec)
                        curr_item = curr_item.to_dict()
                        if impo.item_exists(accession_number, curr_item["identifier"]):
                            logging.info(f"Item with accession_number {accession_number} and identifier {curr_item['identifier']} already exists.")
                            continue
                        else:
                            try:
                                item_obj = Item(
                                    accession_number= accession_number,
                                    filing_type=curr_item["filing_type"],
                                    identifier=curr_item["identifier"],
                                    title=curr_item["title"],
                                    description=curr_item["description"]
                                )
                                item_id = impo.insert_item(item_obj)
                                logging.info(f"Inserted item with ID: {item_id}")
                            except Exception as e:
                                logging.error(f"Error inserting item: {e}")
                                continue  
        except Exception as e:
            logging.error(f"Error processing filing {i + 1}: {e}")
            continue  
    logging.info("Processing completed.")


if __name__ == "__main__":
    main()