"""
Processor package for handling different types of content.
This package contains modules for processing documents, URLs, images, and videos.
"""

# Import all processor functions for easy access
from .document import process_document
from .url import process_url
from .image import process_image
from .video import process_video