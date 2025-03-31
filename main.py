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
    company_folder_names = []  # Initialize with an empty list or provide specific company names
    processed_folder_created = False
    filing_types = ['8-K']
    
    # Step 1: Parse the files
    all_data , filing_type= parse_main(root_path, company_folder_names, processed_folder_created, filing_types)
    # with open("/Users/akshitsanoria/Desktop/PythonP/printing_files/testmainparse.txt", "w") as f:
    #     f.write(all_data)
    # with open("/Users/akshitsanoria/Desktop/PythonP/printing_files/testmain.txt", "w") as f:
    #     for i, data in enumerate(all_data):
    #         f.write(f"{i}: {json.dumps(data, indent=4)} " + "\n")
    logging.info("Parsing completed.")
    itm_path = "/Users/akshitsanoria/Desktop/PythonP/printing_files/clean/item_info.txt"
    # print("priniting keys ")
    impo = Importer()
    impo.create_tables()
    for i in all_data:
        # print(list(i.keys()))
        for j in i:
            print(list(j.keys()))
            comp_data = j["metadata"]["in_filing_data"]
            cleaned_data = clean_main(comp_data, filing_type)
            # for j in i:
            #     for k,v in j.items():
            #         cleaned_data = clean_main(v, filing_type)
            for k,v in cleaned_data.sections.items():
                print(k)
                print(v)
                for curr_sec in v.items:
                    curr_item = v.get_item(curr_sec)
                    curr_item = curr_item.to_dict()
                    try:
                        item_obj = Item(
                            identifier=curr_item["identifier"],
                            title=curr_item["title"],
                            description=curr_item["description"]
                        )
                        item_id = impo.insert_item(item_obj)
                        logging.info(f"Inserted item with ID: {item_id}")
                    except Exception as e:
                        logging.error(f"An error occurred: {e}")

            # for sec, ite in cleaned_data.sections.items():
                # curr_sec = cleaned_data.get_section(sec)
                # curr_item = curr_sec.



    

    
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