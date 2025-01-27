import re
import logging
import unicodedata
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup, Tag, NavigableString
import ftfy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SECFilingParser:
    """Main parser class handling SEC filing processing"""
    
    THEMATIC_BREAK_STYLES = [
        'border-top:Black 4pt solid;border-left:Black 4pt solid;border-bottom:Black 4pt solid',
        'border-bottom:Black 4pt solid',
        'page-break-after:always',
        'width:100%'
    ]

    def __init__(self):
        self.filing_data = {
            'header': {},
            'documents': {},
            'errors': []
        }

    def parse_filing(self, file_path: str) -> Dict:
        """Main entry point for parsing a filing"""
        try:
            soup, is_empty = self.read_document(file_path)
            if is_empty:
                raise ValueError("Empty file provided")

            self.extract_header_data(soup)
            self.process_documents(soup)
            self.normalize_content()
            
            return self.filing_data
        except Exception as e:
            logger.error(f"Fatal error processing {file_path}: {str(e)}")
            self.filing_data['errors'].append(str(e))
            return self.filing_data

    @staticmethod
    def read_document(file_path: str) -> Tuple[BeautifulSoup, bool]:
        """Read and parse document with error handling"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read().strip()
                if not content:
                    return None, True

            for parser in ['lxml', 'html5lib']:
                try:
                    return BeautifulSoup(content, parser), False
                except Exception as e:
                    logger.debug(f"Parser {parser} failed: {str(e)}")
            return None, True
        except UnicodeDecodeError:
            logger.error("Encoding error in file, using lossy decoding")
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                return BeautifulSoup(f.read(), 'html5lib'), False

    def extract_header_data(self, soup: BeautifulSoup) -> None:
        """Extract and validate SEC header information"""
        try:
            sec_header = soup.find(lambda t: t.name and t.name.lower() == 'sec-header')
            if not sec_header:
                raise ValueError("SEC-HEADER not found in document")

            header_text = sec_header.get_text('\n', strip=True)
            self.filing_data['header']['raw'] = header_text

            # Extract accession number with regex pattern
            accession_match = re.search(r'ACCESSION NUMBER:\s*(\S+)', header_text)
            if not accession_match:
                raise ValueError("Accession number not found in header")
            
            self.filing_data['header']['accession_number'] = accession_match.group(1)
            
        except Exception as e:
            logger.error(f"Header processing error: {str(e)}")
            self.filing_data['errors'].append(str(e))

    def process_documents(self, soup: BeautifulSoup) -> None:
        """Process all documents in the filing"""
        try:
            for doc in soup.find_all('document'):
                doc_id = self._get_document_id(doc)
                if not doc_id:
                    continue

                document_data = {
                    'sequence': self._get_tag_text(doc.sequence),
                    'filename': self._get_tag_text(doc.filename),
                    'description': self._get_description(doc),
                    'pages': self._process_pages(doc)
                }
                
                self.filing_data['documents'][doc_id] = document_data
        except Exception as e:
            logger.error(f"Document processing error: {str(e)}")
            self.filing_data['errors'].append(str(e))

    def _process_pages(self, doc: Tag) -> Dict[int, dict]:
        """Process individual document pages with multiple fallback strategies"""
        pages = {}
        try:
            text_tag = doc.find('text')
            if not text_tag:
                return pages

            # Multiple strategies for page splitting
            split_points = self._find_split_points(text_tag)
            
            # If no split points found, use alternative methods
            if not split_points:
                split_points = self._find_alternative_split_points(text_tag)

            # Split document content
            page_content = self._split_content(text_tag, split_points)
            
            for idx, content in enumerate(page_content, 1):
                pages[idx] = {
                    'raw_html': content,
                    'page_number': self._extract_page_number(content),
                    'normalized_text': self._normalize_text(content)
                }
        except Exception as e:
            logger.error(f"Page processing error: {str(e)}")
            self.filing_data['errors'].append(str(e))
            
        return pages

    def _find_split_points(self, element: Tag) -> List[Tag]:
        """Find page split points using multiple strategies"""
        strategies = [
            lambda: element.find_all('hr', style=lambda s: s in self.THEMATIC_BREAK_STYLES),
            lambda: element.find_all('div', style=re.compile(r'border[-a-z]+:Black \d+pt solid')),
            lambda: element.find_all('div', class_=re.compile(r'page-break', re.I)),
            lambda: element.find_all(string=re.compile(r'\bPage \d+\b', re.I))
        ]
        
        for strategy in strategies:
            results = strategy()
            if results:
                return results
        return []

    def normalize_content(self) -> None:
        """Normalize text content across all documents"""
        for doc_id, doc_data in self.filing_data['documents'].items():
            for page_num, page_data in doc_data['pages'].items():
                try:
                    page_data['clean_text'] = self._clean_text(page_data['raw_html'])
                except Exception as e:
                    logger.error(f"Normalization error in {doc_id} page {page_num}: {str(e)}")
                    self.filing_data['errors'].append(str(e))

    @staticmethod
    def _clean_text(raw_html: str) -> str:
        """Robust text cleaning with multiple fallbacks"""
        try:
            # Fix encoding issues
            fixed = ftfy.fix_text(raw_html)
            # Remove control characters
            cleaned = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', fixed)
            # Normalize whitespace
            return ' '.join(cleaned.split())
        except Exception as e:
            logger.error(f"Text cleaning failed: {str(e)}")
            return raw_html  # Return original as fallback

    # Additional helper methods remain similar but with error handling