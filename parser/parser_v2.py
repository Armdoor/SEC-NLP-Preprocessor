import re
import logging
import unicodedata
from typing import Dict, Tuple, Optional
from bs4 import BeautifulSoup, Tag, NavigableString
import ftfy  # For better text normalization

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

##############################################--CLASS BASED STRUCTURE--#################################################

class SECFilingParser:
    def __init__(self):
        self.master_filings: Dict[str, dict] = {}
        self.current_accession: str = ""
        self.thematic_break_styles = [
            'border-top:Black 4pt solid;border-left:Black 4pt solid;border-bottom:Black 4pt solid',
            'border-bottom:Black 4pt solid',
            'border-top:Black 4pt solid;border-left:Black 4pt solid;border-bottom:Black 4pt solid;width:100%',
            'border-bottom:Black 4pt solid;width:100%'
        ]

    def parse_filing(self, file_path: str) -> Dict[str, dict]:
        """Main method to parse an entire SEC filing"""
        soup, is_empty = self.read_document(file_path)
        if is_empty:
            logger.error("Empty file encountered")
            return {}

        header_data = self.extract_header_data(soup)
        if not header_data:
            logger.warning("No valid header data found")
            return {}

        documents_data = self.process_documents(soup)
        normalized_data = self.normalize_documents(documents_data)
        parsed_text = self.extract_all_text(normalized_data)

        return {
            self.current_accession: {
                "header": header_data,
                "documents": normalized_data,
                "full_text": parsed_text
            }
        }

    #############################################--HELPER METHODS--#####################################################

    @staticmethod
    def read_document(file_path: str) -> Tuple[Optional[BeautifulSoup], bool]:
        """Read and parse HTML document with fallback parsers"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return None, True

            for parser in ['lxml', 'html5lib']:
                try:
                    return BeautifulSoup(content, parser), False
                except Exception as e:
                    logger.debug(f"Parser {parser} failed: {str(e)}")
            return None, True
        except Exception as e:
            logger.error(f"File read error: {str(e)}")
            return None, True

    def extract_header_data(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract SEC header information"""
        sec_header = soup.find(lambda t: t.name and t.name.lower() == 'sec-header')
        if not sec_header:
            return {}

        header_text = sec_header.get_text('\n', strip=True)
        accession_match = re.search(r'ACCESSION NUMBER:\s*(\S+)', header_text)
        self.current_accession = accession_match.group(1) if accession_match else ''
        
        return {
            'sec_header': header_text,
            'accession_number': self.current_accession
        }

    def process_documents(self, soup: BeautifulSoup) -> Dict[str, dict]:
        """Process all documents in the filing"""
        documents = {}
        for doc in soup.find_all('document'):
            doc_id = self._get_tag_text(doc.type)
            if not doc_id:
                continue

            documents[doc_id] = {
                'sequence': self._get_tag_text(doc.sequence),
                'filename': self._get_tag_text(doc.filename),
                'description': self._get_description(doc),
                'pages': self._process_document_pages(doc)
            }
        return documents

    def _process_document_pages(self, doc: Tag) -> Dict[int, dict]:
        """Process individual document pages"""
        text_tag = doc.find('text')
        if not text_tag:
            return {}

        pages = []
        current_page = []
        thematic_breaks = self._find_thematic_breaks(text_tag)

        for element in text_tag.children:
            if element in thematic_breaks:
                if current_page:
                    pages.append(current_page)
                    current_page = []
            else:
                current_page.append(str(element))

        if current_page:
            pages.append(current_page)

        return {
            idx + 1: {
                'html': ''.join(page),
                'page_number': self._extract_page_number(page[0]) if page else None
            }
            for idx, page in enumerate(pages)
        }

    def _find_thematic_breaks(self, text_tag: Tag) -> list:
        """Identify page break elements using multiple strategies"""
        breaks = []
        # Check HR tags with specific styles
        breaks += text_tag.find_all('hr', style=lambda s: s in self.thematic_break_styles)
        # Check DIV tags with border styles
        breaks += text_tag.find_all('div', style=re.compile(r'border[-a-z]+:Black \d+pt solid'))
        return breaks

    #############################################--TEXT PROCESSING--#####################################################

    def normalize_documents(self, documents: Dict[str, dict]) -> Dict[str, dict]:
        """Normalize text content for all documents"""
        for doc_id, doc_data in documents.items():
            for page_num, page_data in doc_data['pages'].items():
                cleaned_text = self._clean_text(page_data['html'])
                page_data.update({
                    'normalized_text': cleaned_text,
                    'plain_text': self._html_to_text(page_data['html'])
                })
        return documents

    @staticmethod
    def _clean_text(raw_text: str) -> str:
        """Clean and normalize text content"""
        # Fix common encoding issues
        fixed = ftfy.fix_text(raw_text)
        # Normalize Unicode
        normalized = unicodedata.normalize('NFKC', fixed)
        # Remove extra whitespace
        return re.sub(r'\s+', ' ', normalized).strip()

    @staticmethod
    def _html_to_text(html: str) -> str:
        """Convert HTML content to clean plain text"""
        soup = BeautifulSoup(html, 'lxml')
        
        # Remove unwanted tags
        for tag in ['ix:header', 'script', 'style', 'meta', 'link']:
            for element in soup(tag):
                element.decompose()

        # Handle tables
        for table in soup.find_all('table'):
            rows = ['\t'.join(cell.get_text(strip=True) for cell in row.find_all(['th', 'td']))
                    for row in table.find_all('tr')]
            table.replace_with('\n'.join(rows))

        # Get text with proper spacing
        return soup.get_text('\n', strip=True)

    #############################################--UTILITY METHODS--#####################################################

    @staticmethod
    def _get_tag_text(tag: Optional[Tag]) -> str:
        """Safely extract text from a potentially missing tag"""
        return tag.get_text(strip=True) if tag else ''

    def _get_description(self, doc: Tag) -> str:
        """Extract document description"""
        desc_tag = doc.find('description')
        return ' '.join(desc_tag.stripped_strings) if desc_tag else ''

    @staticmethod
    def _extract_page_number(page_content: str) -> Optional[str]:
        """Extract page number from page content"""
        match = re.search(r'\bPage\s+(\d+)\b', page_content, re.IGNORECASE)
        return match.group(1) if match else None

    def extract_all_text(self, documents: Dict[str, dict]) -> str:
        """Extract consolidated text from all documents"""
        full_text = []
        for doc_id, doc_data in documents.items():
            for page_data in doc_data['pages'].values():
                full_text.append(page_data['plain_text'])
        return '\n\n'.join(full_text)

#############################################--END OF CLASS--###########################################################