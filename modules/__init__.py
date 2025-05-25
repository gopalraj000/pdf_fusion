"""
Professional Document Processor Modules

This package contains all the core functionality modules for the document processing application.
"""

__version__ = "1.0.0"
__author__ = "Professional Document Processor"

# Import main classes for easy access
from .pdf_operations import PDFOperations
from .ocr_processor import OCRProcessor
from .converters import DocumentConverter
from .utilities import UIUtilities, QRGenerator
from .file_manager import FileManager

__all__ = [
    'PDFOperations',
    'OCRProcessor', 
    'DocumentConverter',
    'UIUtilities',
    'QRGenerator',
    'FileManager'
]
