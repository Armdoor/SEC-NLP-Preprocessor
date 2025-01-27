# companies.py (Updated Implementation)
import os
import json
from typing import Dict, List
from parser_V2 import SECFilingParser
import logging

logger = logging.getLogger(__name__)

class FilingProcessor:
    """Handles company-specific filing processing"""
    
    def __init__(self, root_path: str):
        self.root_path = root_path
        self.parser = SECFilingParser()
        self.processed_files = set()

    def process_company(self, company: str, filing_type: str) -> None:
        """Process all filings for a company and filing type"""
        try:
            raw_path = self._get_raw_path(company, filing_type)
            preprocessed_path = self._get_preprocessed_path(company, filing_type)
            
            if not os.path.exists(raw_path):
                logger.warning(f"Missing raw folder for {company}/{filing_type}")
                return

            self._ensure_folder_exists(preprocessed_path)
            self._process_files(raw_path, preprocessed_path, company)

        except Exception as e:
            logger.error(f"Failed processing {company}/{filing_type}: {str(e)}")
            raise

    def _get_raw_path(self, company: str, filing_type: str) -> str:
        """Construct raw file path with validation"""
        path = os.path.join(self.root_path, company, "raw", filing_type)
        if not os.path.isdir(path):
            raise FileNotFoundError(f"Invalid raw path: {path}")
        return path

    def _get_preprocessed_path(self, company: str, filing_type: str) -> str:
        """Construct preprocessed file path"""
        return os.path.join(
            self.root_path, 
            company, 
            "preprocessed", 
            filing_type
        )

    def _ensure_folder_exists(self, path: str) -> None:
        """Create folder hierarchy if missing"""
        os.makedirs(path, exist_ok=True)
        if not os.path.exists(path):
            raise RuntimeError(f"Failed to create directory: {path}")

    def _is_processed(self, output_path: str) -> bool:
        """Check if file already exists with content validation"""
        if not os.path.exists(output_path):
            return False
            
        try:
            with open(output_path, 'r') as f:
                content = json.load(f)
                return bool(content.get('content', {}).get('documents'))
        except (json.JSONDecodeError, KeyError):
            return False

    def _get_text_files(self, folder: str) -> List[str]:
        """Get valid text files with safety checks"""
        try:
            return [
                f for f in os.listdir(folder)
                if f.endswith('.txt') 
                and not f.startswith('._')
                and os.path.isfile(os.path.join(folder, f))
            ]
        except (PermissionError, NotADirectoryError) as e:
            logger.error(f"File access error in {folder}: {str(e)}")
            return []

    def _process_files(self, raw_path: str, preprocessed_path: str, company: str) -> None:
        """Process individual files with cache checking"""
        for file in self._get_text_files(raw_path):
            filing_name = os.path.splitext(file)[0]
            output_path = os.path.join(preprocessed_path, f"{filing_name}_processed.json")

            if self._is_processed(output_path):
                logger.info(f"Skipping already processed file: {file}")
                continue

            try:
                result = self._process_single_file(
                    os.path.join(raw_path, file),
                    output_path,
                    filing_name,
                    company
                )
                self._save_result(result, output_path)
            except Exception as e:
                logger.error(f"Failed processing {file}: {str(e)}")
                raise

    def _process_single_file(self, file_path: str, output_path: str, 
                           filing_name: str, company: str) -> Dict:
        """Process a single filing file"""
        result = self.parser.parse_filing(file_path)
        
        if not result['documents']:
            raise ValueError("No documents found in filing")
            
        return {
            'metadata': {
                'company': company,
                'filing_name': filing_name,
                'accession_number': result['header'].get('accession_number'),
                'processing_errors': result['errors']
            },
            'content': result
        }

    def _save_result(self, result: Dict, output_path: str) -> None:
        """Save results with atomic write operation"""
        try:
            temp_path = f"{output_path}.tmp"
            with open(temp_path, 'w') as f:
                json.dump(result, f, indent=2)
            os.replace(temp_path, output_path)
            logger.info(f"Successfully saved: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save {output_path}: {str(e)}")
            if os.path.exists(temp_path):
                os.remove(temp_path)