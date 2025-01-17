import os
from sec_api import fetch_company_tickers, fetch_company_filings, filter_filings_by_type, create_filings_dataframe,download_filings

from pathlib import Path
import json


# def process_company_filings():
#     company_tickers = fetch_company_tickers()
    
#     filing_types = ["10-K", "10-Q", "8-K", "DEF 14A", "S-1", "13-D"]
#     for key, value in company_tickers.items(): 
#         cik_str = str(value['cik_str']) 
#         ticker = value['ticker'] 
#         company_name = value['title']
#         print(f"Processing filings for {company_name} (CIK: {cik_str})")
        
#         try:
#             filings_metadata = fetch_company_filings(cik_str)
#             df_filings = create_filings_dataframe(filings_metadata, cik_str)
#             filtered_filings = filter_filings_by_type(df_filings, filing_type)
#             company_folder = Path(f"data/{ticker}") 
#             raw_folder = company_folder / "raw" / filing_type
#             preprocessed_folder = company_folder / "preprocessed" / filing_type
#             download_filings(filtered_filings, company_name,cik_str,filing_type)

#             os.makedirs(raw_folder, exist_ok=True)
#             os.makedirs(preprocessed_folder, exist_ok=True)
            
#             with open(company_folder / f"{company_name}_filings_metadata.json", 'w') as file:
#                 json.dump(filings_metadata, file, indent=4) 
            
#             print(f"Saved metadata for {company_name} to {company_folder}")
            
#             for file_name in os.listdir(raw_folder):
#                 raw_file_path = raw_folder / file_name
#                 with open(raw_file_path, 'r') as file:
#                     raw_content = file.read()
                
#                 preprocessed_content = preprocessing_filings(raw_content)
                
#                 # Save the preprocessed content
#                 preprocessed_file_path = preprocessed_folder / (file_name.replace(".html", "_cleaned.txt"))
#                 with open(preprocessed_file_path, 'w') as file:
#                     file.write(preprocessed_content)
                
#                 print(f"Preprocessed and saved {file_name} as cleaned content.")
        
#         except Exception as e:
#             print(f"Error processing {company_name}: {e}")

def process_company_filings():
    # Define the filing types you want to process
    filing_types = ["10-K", "10-Q", "8-K", "DEF 14A", "S-1", "13-D"]
    
    # Fetch the company tickers and metadata
    company_tickers = fetch_company_tickers()
    
    for key, value in company_tickers.items():
        cik_str = str(value['cik_str'])
        ticker = value['ticker']
        company_name = value['title']
        print(f"Processing filings for {company_name} (CIK: {cik_str})")
        
        try:
            # Fetch all filings metadata for the company
            filings_metadata = fetch_company_filings(cik_str)
            df_filings = create_filings_dataframe(filings_metadata, cik_str)
            df_filings.to_csv(os.path.join( f"filtereddf.txt"), sep='\t', index=False)
            # print(f"Saved filtered DataFrame to _filtered.txt")
            # print(df_filings[['accessionNumber', 'filingUrl']])
            # Base directory for storing data
            company_folder = Path(f"data1/{ticker}")
            os.makedirs(company_folder, exist_ok=True)

            # Save filings metadata for the company
            with open(company_folder / f"{company_name}_filings_metadata.json", 'w') as file:
                json.dump(filings_metadata, file, indent=4)
            print(f"Saved metadata for {company_name} to {company_folder}")
            
            # Process each filing type
            for filing_type in filing_types:
                print(f"Processing {filing_type} filings for {company_name}")

                # Filter filings by the filing type
                filtered_filings = filter_filings_by_type(df_filings, filing_type)
                raw_folder = company_folder / "raw" / filing_type
                # filtered_filings.to_csv(os.path.join(raw_folder, f"{ticker}_{filing_type}_filtered.txt"), sep='\t', index=False)
                # print(f"Saved filtered DataFrame to {ticker}_{filing_type}_filtered.txt")
                # Define directory for raw filings
                
                os.makedirs(raw_folder, exist_ok=True)
                
                # Download filings
                download_filings(filtered_filings, ticker, cik_str, filing_type)
                print(f"Downloaded {filing_type} filings for {company_name}")
        
        except Exception as e:
            print(f"Error processing {company_name}: {e}")

    


if __name__ == "__main__":
    process_company_filings()
    # testing()


# def testing():
#     company_tickers = fetch_company_tickers()    
#     filing_type = "10-Q"
#     apple =company_tickers["0"]
#     cik = str(apple["cik_str"]) 
#     ticker = apple["ticker"] 
#     company_name = apple["title"]
#     try:
#         company_filings = fetch_company_filings(cik)
#         df_filings = create_filings_dataframe(company_filings, cik)
#         filings_10q = filter_filings_by_type(df_filings, filing_type)
#         download_filings(filings_10q, company_name,cik,filing_type)
#     except Exception as e:
#         print(f"An error occurred: {e}")
#     company_folder = f"data/{company_name}"
#     raw_folder = os.path.join(company_folder, "raw", filing_type)
#     preprocessed_folder = os.path.join(company_folder, "preprocessed", filing_type)

#     preprocess_and_save(raw_folder, preprocessed_folder)