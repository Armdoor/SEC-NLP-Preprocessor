from file_cleaner import FileCleaner 
# from clean_10k import Clean10k 
from clean_8k import Clean8k 
from Normalization import Normalizer  
from models import *


path = "/Users/akshitsanoria/Desktop/PythonP/data1/AAPL/preprocessed/8-K/filing_1_data.txt"
with open(path, 'r', encoding='utf-8') as file:
    text = file.read()
fc = FileCleaner('8-K', text)


# cd = fc.removefooter(text)
text = fc.remove_metadata()
nr = Normalizer(text)
nr_data = nr.run_norm(text)
# # report = convert_10k(cd)
c8k = Clean8k(nr_data)
report = c8k.data_8k()

with open("/Users/akshitsanoria/Desktop/PythonP/printing_files/clean/structured_8k.txt", "w") as f:
    print("=== Report8K Details ===")
    print("Sections:")
    for num, section in report.sections.items():
        print(f"  {num}: {section.get_item(num)}")  # Assumes `Section` has a `name` attribute
        item_data = f"  {num}: {section.get_item(num)}"
        f.write(f"\n{item_data}\n") 
    # print("\nItems:")
    # if self.item:
    #     for key, value in self.item.items():
    #         print(f"  {key}: {value}")
    # else:
    #     print("  No items found.")
                


# path_8k = "/Users/akshitsanoria/Desktop/PythonP/data1/AAPL/preprocessed/8-K/filing_1_data.txt"
# fc = FileCleaner('8-K', path_8k)
# text = fc.read_file(path_8k)
# # cd = fc.removefooter(text)
# cd = fc.remove_metadata(text)
# # cd = fc.clean_data
# cd =  fc.remove_unnecessary_data(text)
# cd = fc.remove_stopwords(cd) 
# with open("/Users/akshitsanoria/Desktop/PythonP/printing_files/clean/final_data8k.txt", "w") as f:
#     f.write(cd)



