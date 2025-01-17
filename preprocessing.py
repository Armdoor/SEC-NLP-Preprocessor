import os
from bs4 import BeautifulSoup

def preprocessing_filings(raw_content):
    """
    Preprocess an SEC filing document.

    Args:
        raw_content (str): Raw HTML content of the filing.

    Returns:
        str: Cleaned and preprocessed text.
    """
    soup = BeautifulSoup(raw_content, 'html.parser')
    clean_text = soup.get_text(separator='\n')  # Use separator for better formatting
    return clean_text.strip()

def preprocess_company_data(data_folder):
    """
    Iterate through each company folder and preprocess raw filings.

    Args:
        data_folder (str): Path to the main data folder containing company subfolders.

    Returns:
        None
    """
    for company_name in os.listdir(data_folder):
        company_path = os.path.join(data_folder, company_name)
        
        # Skip hidden files or non-directories
        if company_name.startswith('.') or not os.path.isdir(company_path):
            continue
        
        print(f"Processing company: {company_name}")
        
        # Define raw and preprocessed folder paths
        raw_folder = os.path.join(company_path, "raw")
        preprocessed_folder = os.path.join(company_path, "preprocessed")
        
        # Create the preprocessed folder if it doesn't exist
        os.makedirs(preprocessed_folder, exist_ok=True)
        
        # Iterate through filing types inside the raw folder
        for filing_type in os.listdir(raw_folder):
            filing_raw_folder = os.path.join(raw_folder, filing_type)
            
            # Skip hidden files or non-directories
            if filing_type.startswith('.') or not os.path.isdir(filing_raw_folder):
                continue
            
            filing_preprocessed_folder = os.path.join(preprocessed_folder, filing_type)
            
            # Ensure the preprocessed folder for the filing type exists
            os.makedirs(filing_preprocessed_folder, exist_ok=True)
            
            # Process each file in the filing type folder
            for file_name in os.listdir(filing_raw_folder):
                raw_file_path = os.path.join(filing_raw_folder, file_name)
                
                # Skip hidden/system files or non-HTML files
                if file_name.startswith('.') or not file_name.endswith(".html"):
                    print(f"Skipping: {file_name}")
                    continue
                
                with open(raw_file_path, 'r', encoding='utf-8') as raw_file:
                    raw_content = raw_file.read()
                
                # Preprocess the raw content
                clean_text = preprocessing_filings(raw_content)
                
                # Save the preprocessed content
                preprocessed_file_path = os.path.join(filing_preprocessed_folder, file_name.replace(".html", ".txt"))
                with open(preprocessed_file_path, 'w', encoding='utf-8') as preprocessed_file:
                    preprocessed_file.write(clean_text)
                
                print(f"Processed and saved: {file_name} -> {filing_type}/{file_name.replace('.html', '.txt')}")

if __name__ == "__main__":
    # Path to your main data folder
    main_data_folder = "data"
    
    preprocess_company_data(main_data_folder)
