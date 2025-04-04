from Cleaner.insert_data import *


importer = Importer()


try:
        
    importer.delete_item(1)
    importer.delete_item(2)
    importer.delete_item(3)
    importer.delete_item(4)
except Exception as e:
    logging.error(f"An error occurred: {e}")

