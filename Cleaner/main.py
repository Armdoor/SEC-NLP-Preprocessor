"""
Main for cleaning the data 
"""
from .file_cleaner import FileCleaner
from .clean_8k import Clean8k 
from .clean_10k import Clean10k as c10k
# from .Normalization import Normalizer as nr
from .models import *
# from .insert_data import Importer as imp
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

def clean_data(comp_data, filing_type):
    # Process the comp_data dictionary using the FileCleaner class
    print("priniting keys ")
    # for k,v in comp_data.items():
    #     print(k)
    # filing_type = comp_data['json_data']['filing_type']
    cleaner = FileCleaner(filing_type, comp_data)
    cleaned_data = cleaner.remove_metadata()
    print("cleaned data: ", cleaned_data[:50])
    # Additional cleaning and processing steps
    if filing_type == '8-K':
        c8k = Clean8k(cleaned_data)
        report = c8k.data_8k()
        # imp.insert_report8K(report)
    elif filing_type == '10-K':
        report = c10k(cleaned_data)
        # imp.insert_report10K(report)
    print("Type of report: ", type(report) )
    return report
        

    # # Normalization
    # normalizer = Normalization(comp_data)
    # normalizer.normalize()

    # # Model processing
    # model = Model(comp_data)
    # model.process()

    # # Insert data into the database
    # inserter = InsertData(comp_data)
    # inserter.insert()
# def main():
#      with ThreadPoolExecutor(max_workers=10) as executor:
#          future_to_comp_data = {executor.submit(clean_data, comp_data): comp_data for comp_data in comp_data_list}

#          for future in as_completed(future_to_comp_data):
#              try:
#                  future.result()
#              except Exception as e:
#                  logging.error(f"Error cleaning data: {str(e)}", exc_info=True)

# if __name__ == "__main__":
#     # Example usage
#     comp_data_list = []  # This should be populated with the data to be cleaned
#     main(comp_data_list)




"""
File cleaner ->  nomalizer-> clean 10k or clean 8k  -> insert_data 

"""