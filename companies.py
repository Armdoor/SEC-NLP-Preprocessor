import os
from parser import parser8k
root_path = "/Volumes/T7/data"

def company_folders(root_path):
# Get all folder names
    folder_names = [name for name in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, name))]

    if type(folder_names) == type(None):                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
        print("No folders found in the path")
        return None

    # folder_names = folder_names.sort()
    with open("companies.txt", "w") as file:
        for folder_name in folder_names:
            file.write(folder_name + "\n")                          
    return folder_names

def create_preprocessed_folders(folder_names, root_path):
    if folder_names is None:
        print("No folders found in the path for creating preprocessed folders")
        return None
    for folder_name in folder_names:
        create_folder_at_path = os.path.join(root_path, folder_name, "preprocessed")
        os.makedirs(create_folder_at_path, exist_ok=True)



# folder_names = company_folders(root_path)
# create_preprocessed_folders(folder_names, root_path)


def process_text_files(root_path):
    # i = 0
    # for company_folder in company_folders:
    #     target_folder = os.path.join(root_path, company_folder, "raw", "8-K")
    #     if not os.path.exists(target_folder):  
    #         print(f"Path does not exist: {target_folder}")
    #         continue /raw/8-K
    target_folder = os.path.join(root_path, "raw", "8-K")
    if not os.path.exists(target_folder):  
        print(f"Path does not exist: {target_folder}")
        
    text_files = [
        file for file in os.listdir(target_folder) 
        if file.endswith(".txt") and not file.startswith("._")  # Skip ._ files
    ]
    create_folder_at_path = os.path.join(root_path, "preprocessed", "8-K")
    os.makedirs(create_folder_at_path, exist_ok=True)
    preprocessed_path = create_folder_at_path
    # print("Caompany folder: ", company_folder)
    for text_file in text_files:
        file_path = os.path.join(target_folder, text_file)
        print("File path: ", file_path)
        filing_name = text_file.split(".")[0]
        print("Parsing filing ", filing_name)
        # print("File path: ", file_path)
        parser8k.main_8k(file_path, filing_name, preprocessed_path)
            
        
            
# comapnt_path
# Call the function
cmp_path = "/Volumes/T7/data/AAPL"
process_text_files(cmp_path)