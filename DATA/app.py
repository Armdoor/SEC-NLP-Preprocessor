from db_setup import *
from models import *
from clean_10k import *
from clean_8k import *

# def main_call():
#     path = "/Users/akshitsanoria/Desktop/PythonP/printing_files/item1_8k.txt"
#     report8k = Report8K()
#     data_8k(report8k, path)
#     import_8k = CleanedData()

#     sect = report8k.get_all_section()
#     if sect is not None:
#         print(type(sect))
#         for key, value in sect.items():
#             curr_sec = value
#             curr_items = curr_sec.get_all_items()

#             for k,v in curr_items.items():
#                 print("type of k", type(k))
#                 print("type of v", type(v))
#                 # print(v.to_dict())

    
#         print(report8k is None)
#     import_8k.insert_report8K(report8k)

# main_call()

"""
Report8K -> 
"""

def main_10k():
    