import os
from concurrent.futures import ThreadPoolExecutor
from typing import List
from companies_V2 import FilingProcessor
import logging

logger = logging.getLogger(__name__)
# parser.py (Updated SECFilingParser Class)
class SECFilingParser:
    def __init__(self):
        # Previous initialization
        self.filing_data = {
            'header': {},
            'documents': {},
            'errors': []
        }

    def _get_document_id(self, doc: Tag) -> Optional[str]:
        """Extract document ID with validation"""
        try:
            doc_type = doc.find('type')
            if not doc_type:
                logger.warning("Document missing type tag")
                return None
                
            doc_id = doc_type.get_text(strip=True)
            if not doc_id:
                logger.warning("Empty document ID found")
                return None
                
            return doc_id
        except Exception as e:
            logger.error(f"Document ID extraction failed: {str(e)}")
            self.filing_data['errors'].append(str(e))
            return None

    def _get_tag_text(self, tag: Optional[Tag]) -> str:
        """Safely extract text from a potentially missing tag"""
        try:
            return tag.get_text(strip=True) if tag else ''
        except AttributeError:
            return ''

    def _get_description(self, doc: Tag) -> str:
        """Robust description extraction"""
        try:
            desc_tag = doc.find('description')
            if not desc_tag:
                return ''
                
            # Handle both string and tag contents
            parts = []
            for content in desc_tag.contents:
                if isinstance(content, str):
                    parts.append(content.strip())
                elif content.name == 'text':
                    break
                else:
                    parts.append(content.get_text(' ', strip=True))
                    
            return ' '.join(parts)
        except Exception as e:
            logger.error(f"Description extraction failed: {str(e)}")
            return ''

    def _process_pages(self, doc: Tag) -> Dict[int, dict]:
        """Enhanced page processing with fallback"""
        pages = {}
        try:
            text_tag = doc.find('text')
            if not text_tag:
                logger.warning("Document contains no text tag")
                return pages

            # Fallback: Use entire content if no splits found
            content = str(text_tag)
            split_points = self._find_split_points(text_tag)
            
            if not split_points:
                logger.info("No split points found, using single page")
                pages[1] = self._create_page_entry(content)
                return pages

            # Split content using found points
            page_content = self._split_content(text_tag, split_points)
            
            for idx, content in enumerate(page_content, 1):
                pages[idx] = self._create_page_entry(content)
                
        except Exception as e:
            logger.error(f"Page processing failed: {str(e)}")
            self.filing_data['errors'].append(str(e))
            
        return pages

    def _create_page_entry(self, content: str) -> dict:
        """Create standardized page entry"""
        return {
            'raw_html': content,
            'page_number': self._extract_page_number(content),
            'normalized_text': self._normalize_text(content),
            'processing_errors': []
        }

    def _extract_page_number(self, content: str) -> Optional[int]:
        """Robust page number extraction with multiple patterns"""
        patterns = [
            r'Page (\d+)',
            r'\bPg?\.? (\d+)\b',
            r'\bPage:? (\d+)\b',
            r'^(\d+)$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue
        return None

    def _split_content(self, text_tag: Tag, split_points: List[Tag]) -> List[str]:
        """Split document content with multiple strategies"""
        try:
            # Convert BeautifulSoup tag to string
            content_str = str(text_tag)
            
            # Create split pattern
            pattern = '|'.join(re.escape(str(point)) for point in split_points)
            
            # Split using positive lookahead to keep split markers
            return re.split(f'({pattern})', content_str)
            
        except Exception as e:
            logger.error(f"Content splitting failed: {str(e)}")
            return [str(text_tag)]