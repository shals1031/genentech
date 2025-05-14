"""
Module for processing document files (PDF and TXT) using VertexAI.
This module provides functionality to read document files and analyze them using VertexAI.
"""

import os
from typing import Iterator
from vertexai.generative_models import Part

from ai_service import analyze_content_with_gemini

def read_document_file(file_path: str) -> tuple[bytes, str]:
    """
    Read a document file (PDF or TXT) and return its contents as bytes and the file type.

    Args:
        file_path: Path to the document file

    Returns:
        A tuple containing the contents of the document file as bytes and the file type
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    file_extension = os.path.splitext(file_path)[1].lower()

    with open(file_path, "rb") as file:
        file_data = file.read()

    if file_extension == '.pdf':
        file_type = "application/pdf"
    elif file_extension == '.txt':
        file_type = "text/plain"
    else:
        raise ValueError(f"Unsupported file type: {file_extension}. Only PDF and TXT files are supported.")

    return file_data, file_type

def process_document(
    file_path: str,
    country:str,
) -> Iterator[str]:
    """
    Process a document file (PDF or TXT) using VertexAI.

    Args:
        file_path: Path to the document file
        prompt: The prompt to send to the model
        system_instruction: The system instruction for the model

    Returns:
        An iterator of response chunks from the model
    """
    # Read the document file
    document_data, file_type = read_document_file(file_path)

    # Create content parts for analysis
    content_parts = [
        Part.from_data(document_data, file_type)
    ]

    # Analyze the content using VertexAI Gemini Model
    return analyze_content_with_gemini(
        content_parts=content_parts,
        country = country
    )
