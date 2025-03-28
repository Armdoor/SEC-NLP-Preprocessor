from Cleaner.file_cleaner import FilingCleaner

def celaner(parsed_pages, filing_type):
    cleaner = FilingCleaner()
    parsed_pages = cleaner.clean_data(parsed_pages)
    if filing_type == '10-K':
        parsed_pages = cleaner.clean_10k_filing(parsed_pages)
    else:
        parsed_pages = cleaner.remove_unnecessary_data_8k(parsed_pages)
    