import requests
import time
from bs4 import BeautifulSoup


def parse_main_website(cik: str):

    # URL of the website you want to parse
    url = "https://www.sec.gov/edgar/browse/?CIK={cik}&owner=exclude"

    # Send a GET request to the website
    response = requests.get(url)
    time.sleep(5)
    print(response.text)
    # Parse the HTML content of the webpage
    # soup = BeautifulSoup(response.content, "html.parser")

    # # Find all anchor tags with href attributes
    # div_tag = soup.find('div', {'id': 'entityInformation'})
    # # Print all the links
    # if div_tag: 
    #     data = div_tag.decode_contents() 
    #     print(data) 
    # else: print("Tag not found.")


parse_main_website("1045810")