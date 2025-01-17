import requests
import pandas as pd
import os
import time
import json
import shutil

def fetch_company_tickers():
    """
    Fetch the company tickers and their corresponding CIKs from SEC's JSON file.
    
    Returns:
        dict: A dictionary of company names and their CIKs.
    """
    headers = {
    'User-Agent': 'Akshit Sanoria (armdoor7457@gmail.com) PythonScript for Research/Non-Commercial Use',
    'Accept-Encoding': 'gzip, deflate',
    'Host': 'www.sec.gov'
}
    url = "https://www.sec.gov/files/company_tickers.json"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch company tickers. HTTP {response.status_code}")

def fetch_company_filings(cik: str):
    """
    Fetch all filings metadata for a company using the SEC EDGAR API.
    """
    cik = cik.zfill(10)  # Ensure CIK is 10 digits
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    headers = {'User-Agent': "Akshit Sanoria (armdoor7457@gmail.com) PythonScript for Research/Non-Commercial Use"}

    response = requests.get(url, headers=headers)
    time.sleep(0.1)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch filings metadata. HTTP {response.status_code}: {response.text}")

    return response.json()


# def fetch_company_filings(cik: str, max_retries=5):
#     """
#     # Fetch all filings metadata for a company using the SEC EDGAR API with dynamic delay handling.
#     """
#     cik = cik.zfill(10)  # Ensure CIK is 10 digits
#     url = f"https://data.sec.gov/submissions/CIK{cik}.json"
#     headers = {
#     'User-Agent': 'Akshit Sanoria (armdoor7457@gmail.com) PythonScript for Research/Non-Commercial Use',
#     'Accept-Encoding': 'gzip, deflate',
#     'Host': 'www.sec.gov'
#     }
#     retries = 0
#     delay = 1  # Initial delay (100 ms)
    
#     while retries < max_retries:
#         response = requests.get(url, headers=headers)
        
#         if response.status_code == 200:
#             return response.json()
#         elif response.status_code == 429:  # Rate limit exceeded
#             print(f"Rate limit hit. Retrying in {delay} seconds...")
#             time.sleep(delay)  # Wait before retrying
#             delay *= 2  # Exponential backoff
#             retries += 1
#         else:
#             raise Exception(f"Failed to fetch filings metadata. HTTP {response.status_code}: {response.text}")
    
#     raise Exception("Max retries reached. Unable to fetch filings metadata.")

def create_filings_dataframe(filings_metadata, cik):
    """
    Create a pandas DataFrame from the filings metadata and add the filing URL.
    """
    filings = filings_metadata.get("filings", {}).get("recent", {})
    filings_df = pd.DataFrame(filings)
    # filings_df.to_csv(os.path.join( f"filtereddf.txt"), sep='\t', index=False)
    # print(f"Saved filtered DataFrame to _filtered.txt")
    # Add filing URL column
    filings_df["filingUrl"] = filings_df.apply(
        lambda row: f"https://www.sec.gov/Archives/edgar/data/{cik}/{row['accessionNumber'].replace('-', '')}/{row['accessionNumber']+'.txt'}",
        axis=1
    )
    # print(filings_df["filingUrl"])
    
    return filings_df


def filter_filings_by_type(filings_df, filing_type):
    """
    Filter the filings DataFrame by filing type.
    """
    return filings_df[filings_df["form"] == filing_type]


def save_to_file(df, filename, sep="\t"):
    """
    Save the DataFrame to a file (CSV or TXT).
    """
    df.to_csv(filename, sep=sep, index=False)
    print(f"Filtered filings saved to {filename}")


def download_filings(filtered_df, ticker, cik, filing_type):
    """
    Download filings from the given list of links and save them locally.

    Args:
        links (list): List of URLs to the filings.
        output_dir (str): Directory where filings will be saved.

    Returns:
        None
    """
    headers = {
    'User-Agent': 'Akshit Sanoria (armdoor7457@gmail.com) PythonScript for Research/Non-Commercial Use',
    'Accept-Encoding': 'gzip, deflate',
    'Host': 'www.sec.gov'
}
    company_folder = f"data1/{ticker}"
    raw_folder = os.path.join(company_folder, "raw", filing_type)
    os.makedirs(raw_folder, exist_ok=True)



    max_requests_per_second = 10 
    request_interval = 1 / max_requests_per_second
    filtered_df["filingUrl"].to_csv(os.path.join( f"filtereddfurl.txt"), sep='\t', index=False)
    for index, row in filtered_df.iterrows():
        filing_url = row['filingUrl']
        file_name = f"filing_{index + 1}.txt"
        file_path = os.path.join(raw_folder, file_name)
        
        try:
            raw_content = requests.get(filing_url, headers=headers, timeout=10)
            raw_content.raise_for_status()  # Raise exception for HTTP errors
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(raw_content.text)
            print(f"Downloaded raw filing: {file_name} for {ticker} (CIK: {cik})")
        except Exception as e:
            print(f"Failed to download filing {index + 1}: {e}")
        
        # Add a delay between requests
        time.sleep(request_interval)  

# name_list =[]

def getNames():
    name_json = fetch_company_tickers()
    names = []
    for key in name_json: 
        names.append(name_json[key]['title'])
    return names

# if __name__ == "__main__":
#     name_list =getNames()
#     directory = '/Users/akshitsanoria/Desktop/PythonP/data'
#     # List all folders in the directory 
#     all_folders = [f.name for f in os.scandir(directory) if f.is_dir()] 
#     # Folders that exist in the name_list 
#     existing_folders = [name for name in name_list if name in all_folders] 
#     # Folders that are in the directory but not in the name_list 
#     extra_folders = [folder for folder in all_folders if folder not in name_list] 
#     # Write the results to files 
#     with open('existing_folders.txt', 'w') as file:
#         for folder in existing_folders: 
#             file.write(f"{folder}\n") 
    
#     with open('extra_folders.txt', 'w') as file: 
#         for folder in extra_folders: 
#             file.write(f"{folder}\n")
#     for folder in extra_folders: 
#         folder_path = os.path.join(directory, folder)
#         shutil.rmtree(folder_path)
# Main script
# if __name__ == "__main__":
# cik = "1045810"  # Example CIK for NVIDIA
# filing_type = "10-K"  # Example filing type


# # #         # Fetch and process filings
# filings_metadata = fetch_company_filings(cik)
# filings_df = create_filings_dataframe(filings_metadata, cik)
# filtered_df = filter_filings_by_type(filings_df, filing_type)

# # #         # Save filtered data to a file
# save_to_file(filtered_df, "filings_url.txt", sep="\t")
# output_directory = "./filings"
# filing_links = filtered_df["filingUrl"].tolist()
# download_filings(filtered_df,'NVDA', cik, filing_type)
# def download_filings(filtered_df, ticker, cik, filing_type):
#     except Exception as e:
#         print(f"An error occurred: {e}")


# company_tickers = fetch_company_tickers()
# print(len(company_tickers))
# print(company_tickers[1])
# cik = "1045810"
# dt = fetch_company_filings(cik)
# with open('dt.txt', 'w', encoding='utf-8') as file: 
#     json.dump(dt, file, indent=4)
# filings_df = create_filings_dataframe(dt, cik)
# filtered_df = filter_filings_by_type(filings_df, "10-Q")
# filtered_df.to_csv('dataframe.txt', sep='\t', index=False, header=True, mode='w')
# download_filings(filtered_df, "Nvda", cik, "10-K")