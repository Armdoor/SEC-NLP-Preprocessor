"""
A top-level script to run the entire pipeline.

"""
import json
import logging 
from sec_parser.parser_main import main as parse_main
from Cleaner.main import clean_data as clean_main






def main():
    root_path = '/Users/akshitsanoria/Desktop/PythonP/testing'
    company_folder_names = []  # Initialize with an empty list or provide specific company names
    processed_folder_created = False
    filing_types = ['8-K']
    
    # Step 1: Parse the files
    all_data = parse_main(root_path, company_folder_names, processed_folder_created, filing_types)
    # with open("/Users/akshitsanoria/Desktop/PythonP/printing_files/testmainparse.txt", "w") as f:
    #     f.write(all_data)
    with open("/Users/akshitsanoria/Desktop/PythonP/printing_files/testmain.txt", "w") as f:
        for i, data in enumerate(all_data):
            f.write(f"{i}: {json.dumps(data, indent=4)} " + "\n")
    logging.info("Parsing completed.")
    print("priniting keys ")
    for i in all_data:
            for j in i:
                for k,v in j.items():
                    cleaned_data = clean_main(v)
                    # insert_data(cleaned_data)
    # for i, data in enumerate(all_data):
    #     for filing in data:
    #         try:
    #             # Clean the data
    #             cleaned_data = clean_main(filing)
    #             logging.info(f"Successfully processed and pushed filing {i} to the database.")
    #         except Exception as e:
    #             logging.error(f"Failed to process filing {i}: {str(e)}", exc_info=True)
   
    # logging.info("Cleaning completed.")


if __name__ == "__main__":
    main()