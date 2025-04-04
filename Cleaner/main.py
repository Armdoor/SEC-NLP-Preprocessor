"""
Main for cleaning the data 
"""
from .file_cleaner import FileCleaner
from .clean_8k import Clean8k 
from .clean_10k import Clean10k as c10k
from .models import *
import logging

def clean_data(comp_data, filing_type, accession_number):
    
    # Process the comp_data dictionary using the FileCleaner class
    cleaner = FileCleaner(filing_type, comp_data)
    cleaned_data = cleaner.remove_metadata()

    # Additional cleaning and processing steps
    if filing_type == '8-K':
        c8k = Clean8k(cleaned_data, accession_number, filing_type)
        report = c8k.data_8k()

    elif filing_type == '10-K':
        report = c10k(cleaned_data)

    return report
        





"""
File cleaner ->  nomalizer-> clean 10k or clean 8k  -> insert_data 

"""