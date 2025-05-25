# src/processing/pdf_processor.py
import io
import logging
from pathlib import Path
from typing import List, Optional, Union
import PyPDF2
from src.config import Config

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Handle PDF file processing and text extraction"""
    
    def __init__(self):
        self.max_file_size = Config.MAX_FILE_SIZE_MB * 1024 * 1024  # Convert to bytes
    
    def extract_text_from_file(self, file_path: Union[str, Path]) -> Optional[str]:
        """Extract text from a PDF file on disk"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.error(f"File does not exist: {file_path}")
                return None
            
            if file_path.stat().st_size > self.max_file_size:
                logger.error(f"File too large: {file_path.stat().st_size} bytes")
                return None
            
            with open(file_path, 'rb') as file:
                return self._extract_text_from_stream(file)
                
        except Exception as e:
            logger.error(f"Error processing PDF file {file_path}: {str(e)}")
            return None
    
    def extract_text_from_uploaded_file(self, uploaded_file) -> Optional[str]:
        """Extract text from a Streamlit uploaded file object"""
        try:
            if uploaded_file.size > self.max_file_size:
                logger.error(f"Uploaded file too large: {uploaded_file.size} bytes")
                return None
            
            # Reset file pointer to beginning
            uploaded_file.seek(0)
            return self._extract_text_from_stream(uploaded_file)
            
        except Exception as e:
            logger.error(f"Error processing uploaded PDF: {str(e)}")
            return None
    
    def _extract_text_from_stream(self, file_stream) -> Optional[str]:
        """Extract text from a file stream"""
        try:
            pdf_reader = PyPDF2.PdfReader(file_stream)
            
            if len(pdf_reader.pages) == 0:
                logger.warning("PDF has no pages")
                return None
            
            text_content = []
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        text_content.append(page_text)
                    else:
                        logger.warning(f"No text extracted from page {page_num + 1}")
                        
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num + 1}: {str(e)}")
                    continue
            
            if not text_content:
                logger.error("No text could be extracted from PDF")
                return None
            
            full_text = "\n\n".join(text_content)
            
            # Basic text cleaning
            full_text = self._clean_text(full_text)
            
            logger.info(f"Successfully extracted {len(full_text)} characters from PDF")
            return full_text
            
        except Exception as e:
            logger.error(f"Error reading PDF: {str(e)}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:  # Keep non-empty lines
                cleaned_lines.append(line)
        
        # Join lines with single newlines
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Remove excessive spaces
        import re
        cleaned_text = re.sub(r' +', ' ', cleaned_text)
        
        return cleaned_text
    
    def save_uploaded_file(self, uploaded_file, filename: Optional[str] = None) -> Optional[Path]:
        """Save uploaded file to uploads directory"""
        try:
            if filename is None:
                filename = uploaded_file.name
            
            # Ensure filename is safe
            filename = self._sanitize_filename(filename)
            file_path = Config.UPLOAD_DIR / filename
            
            # Handle filename conflicts
            counter = 1
            original_stem = file_path.stem
            while file_path.exists():
                file_path = Config.UPLOAD_DIR / f"{original_stem}_{counter}{file_path.suffix}"
                counter += 1
            
            # Save file
            uploaded_file.seek(0)
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.read())
            
            logger.info(f"Saved uploaded file to: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving uploaded file: {str(e)}")
            return None
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe storage"""
        import re
        
        # Keep only alphanumeric, dots, hyphens, underscores
        filename = re.sub(r'[^\w\-_.]', '_', filename)
        
        # Ensure PDF extension
        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'
        
        return filename
    
    def get_file_info(self, file_path: Union[str, Path]) -> dict:
        """Get information about a PDF file"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return {"error": "File does not exist"}
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                return {
                    "filename": file_path.name,
                    "size_bytes": file_path.stat().st_size,
                    "size_mb": round(file_path.stat().st_size / (1024 * 1024), 2),
                    "num_pages": len(pdf_reader.pages),
                    "has_text": any(page.extract_text().strip() for page in pdf_reader.pages[:3])  # Check first 3 pages
                }
                
        except Exception as e:
            return {"error": f"Error reading file info: {str(e)}"}

