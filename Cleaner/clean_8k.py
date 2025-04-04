from .models import *
import re
from .Normalization import Normalizer


FILINGS ={
    "Item 1.01" : "Entry into a Material Definitive Agreement",
    "Item 1.02" : "Termination of a Material Definitive Agreement",
    "Item 1.03" : "Bankruptcy or Receivership",
    "Item 2.01" : "Completion of Acquisition or Disposition of Assets",
    "Item 2.02" : "Results of Operations and Financial Condition",
    "Item 2.03" : "Creation of a Direct Financial Obligation or an Obligation under an Off-Balance Sheet Arrangement of a Registrant",
    "Item 2.04" : "Triggering Events That Accelerate or Increase a Direct Financial Obligation or an Obligation under an Off-Balance Sheet Arrangement",
    "Item 2.05" : "Costs Associated with Exit or Disposal Activities",
    "Item 2.06" : "Material Impairments",
    "Item 3.01" : "Notice of Delisting or Failure to Satisfy a Continued Listing Rule or Standard; Transfer of Listing",
    "Item 3.02" : "Unregistered Sales of Equity Securities",
    "Item 3.03" : "Material Modification to Rights of Security Holders",
    "Item 4.01" : "Changes in Registrant’s Certifying Accountant",
    "Item 4.02" : "Non-Reliance on Previously Issued Financial Statements or a Related Audit Report or Completed Interim Review",
    "Item 5.01" : "Changes in Control of Registrant",
    "Item 5.02" : "Departure of Directors or Certain Officers; Election of Directors; Appointment of Certain Officers; Compensatory Arrangements of Certain Officers",
    "Item 5.03" : "Amendments to Articles of Incorporation or Bylaws; Change in Fiscal Year",
    "Item 5.05" : "Amendments to the Registrant’s Code of Ethics, or Waiver of a Provision of the Code of Ethics",
    "Item 5.07" : "Submission of Matters to a Vote of Security Holders ",
    "Item 7.01" : "Regulation FD",
    "Item 8.01" : "Other Events",
    "Item 9.01" : "Financial Statements and Exhibits"
}
FILINGS_KEYS = list(FILINGS.keys())


class Clean8k:

    def __init__(self, text, accession_number, filing_type):
        self.text = text
        self.accession_number = accession_number
        self.filing_type = filing_type

    def structure_of_8k(self, text, report):
       
        
        # Improved regex to match item headers like "Item 2.02", "Item 9.01", etc.
        # item_pattern = re.compile(
        #     r'\bItem\s+(\d+\.\d+)\b[:\s]*(.*?)(?=\.\s|$)', 
        #     re.IGNORECASE | re.DOTALL
        # )
        normalizer = Normalizer(text)
        # matches = list(item_pattern.finditer(text))
        # text = normalizer.clean_text(text)
        # text = normalizer.remove_unnecessary_data(text)
        # text = normalizer.remove_stopwords(text)
        pattern = r'(Item\s\d+\.\d+)\s([^\n.]+)(?:\.\s)?'
        matches = re.finditer(pattern, text)
        item_num_pattern = r"[0-9]\.[0-9]*"   
        for i, match in enumerate(matches):

            gr =  match.group(0)
            item = re.findall(item_num_pattern, gr) 
            item_num = item[0]
            item_key = "Item " + item_num
            if item_key in FILINGS_KEYS:
                item_title = FILINGS[item_key]
                content_start = match.end()  
                next_text = text[content_start:]
                next_item = re.search(pattern, next_text)
                if next_item:
                    end_idx = next_item.start() + content_start
                    split_idx = next_item.start()
                    content = text[content_start:end_idx].strip()
                    nxt = text[end_idx:].strip()
                else:
                    content = text[content_start:].strip()
                    nxt=''
                section_num = int(item_num.split('.')[0])
                if section_num not in report.sections:
                    report.add_section(section_num)
                section = report.get_section(section_num)
                new_item = self.create_item(item_num, item_title, content)
                section.add_item(item_num, new_item)


        # for i, match in enumerate(matches):
        #     item_number = match.group(1).strip()
        #     item_title = match.group(2).strip()
        #     print("item title", item_title)
        #     # item_content = match.group(0).strip()  # Entire matched text (header + content)
        #     start_index = match.end()  # Start after the current match
        #     end_index = text.find("Item", start_index)  # Find the next "Item"
        #     if end_index == -1:  # If no next "Item", take the rest of the text
        #         end_index = len(text)
        #     item_content = text[start_index:end_index].strip()
        #     print("item content", item_content)
        #     # Extract section number (e.g., "2" from "2.02")
        #     section_number = int(item_number.split('.')[0])

        #     # Add section to report if not already present
        #     if section_number not in report.sections:
        #         report.add_section(section_number)
        #     section = report.get_section(section_number)

        #     # Create and add the item
        #     new_item = self.create_item(item_number, item_title, item_content)
        #     section.add_item(item_number, new_item)

    def create_item(self, item_number, item_title, item_content):
        """
        Creates an Item object with the given number, title, and content.
        """
        return Item(self.accession_number, self.filing_type ,item_number, item_title, description=item_content)


# path= "/Users/akshitsanoria/Desktop/PythonP/data1/AAPL/preprocessed/8-K/filing_977_data.txt"
    def data_8k(self):
            # with open(path, "r") as f:
            #     text = f.read()
        report = Report8K()
        self.structure_of_8k(self.text, report)
        return report
# data_8k(path)
    # print(report.__repr__())
    # rep = report.get_section(2)
    # print(rep)
    # if rep:
    #     item1 = rep.items.get("2.05")
    #     with open("/Users/akshitsanoria/Desktop/PythonP/printing_files/item1_8k.txt", "w") as f:
    #         f.write(item1.description)

# with open("/Users/akshitsanoria/Desktop/PythonP/Testing_Folder/AAPL/preprocessed/8-K/filing_15_data.txt", "r") as f:
#     text = f.read()
# clean = Clean8k(text)
# clean.data_8k()

# path= "/Users/akshitsanoria/Desktop/PythonP/data1/AAPL/preprocessed/8-K/filing_43_data.txt"
# an = "0001193125-14-275598"
# ft = "8-K"
# with open(path, 'r') as f:
#     t = f.read()
# cl = Clean8k(t,an, ft)
# rep = Report8K()
# cl.structure_of_8k(t, rep)