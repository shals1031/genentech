"""
Module for interacting with AI services.
This module provides functionality to analyze content using VertexAI (Gemini).
"""

import configuration
import base64
import requests
import json
import io
from typing import Iterator, Optional, Union, List, Dict, Any
import PyPDF2
import vertexai
from vertexai.generative_models import GenerativeModel, Content, Part

# Initialize VertexAI
vertexai.init(project=configuration.PROJECT_ID, location=configuration.VERTEXT_AI_REGION_NAME)

def extract_text_from_pdf(pdf_data):
    """
    Extract text from PDF binary data.

    Args:
        pdf_data: Binary data of the PDF file

    Returns:
        Extracted text from the PDF
    """
    pdf_text = ""
    try:
        # Create a PDF file reader object
        pdf_file = io.BytesIO(pdf_data)
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        # Extract text from each page
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            pdf_text += page.extract_text() + "\n\n"

        if not pdf_text.strip():
            pdf_text = "[PDF content could not be extracted. The PDF might be scanned or contain only images.]"
    except Exception as e:
        pdf_text = f"[Error extracting PDF content: {str(e)}]"

    return pdf_text

    def _create_prompts(self, country):
        """Create custom prompts based on country."""
        prompt = f"Based on official medical norms in {country}, determine whether the content is compliant. If the content is not compliant, identify and highlight the specific parts of the document that violate the regulations."
        system_instruction = f"You are a senior compliance officer for pharmaceutical regulations in {country}. Your task is to analyze the provided content and determine whether it complies with official medical norms in {country}."

        return prompt, system_instruction

def analyze_content_with_gemini(
    content_parts: List[Union[str, Part]],
    country:str
) -> Iterator[str]:
    """
    Analyze content using VertexAI (Gemini).

    Args:
        content_parts: List of content parts to analyze (text or Part objects)
        prompt: The prompt to send to the model
        system_instruction: The system instruction for the model

    Returns:
        An iterator of response chunks from the model
    """
    # Initialize the Gemini model
    model = GenerativeModel(configuration.MODEL_NAME)

    # Create a chat session
    chat = model.start_chat()

    system_instruction = f"""
                You are a senior compliance officer for pharmaceutical regulations in {country}. 
                Your task is to analyze the provided content and determine whether it complies with official medical norms in {country}.
                """

    prompt = f"""
              Based on official medical norms in {country}, determine whether the content is compliant. 
              If the content is not compliant, identify and highlight the specific parts of the document that violate the regulations.
              """

    # Create the user message with system instruction, prompt and content parts
    user_message_parts = [
        Part.from_text(f"System instruction: {system_instruction}\n\nAnalyze the following content:\n\n{prompt}")
    ]

    # Process content parts
    for part in content_parts:
        if isinstance(part, str):
            user_message_parts.append(Part.from_text(part))
        elif isinstance(part, Part):
            user_message_parts.append(part)
        elif isinstance(part, dict):
            if part.get("type") == "text":
                user_message_parts.append(Part.from_text(part.get("text", "")))
            elif part.get("type") == "binary" and part.get("mime_type") == "application/pdf" and part.get("data"):
                # For PDF, decode the base64 data and extract text
                pdf_binary_data = base64.b64decode(part.get("data"))
                extracted_text = extract_text_from_pdf(pdf_binary_data)
                user_message_parts.append(Part.from_text(extracted_text))
            elif part.get("type") == "binary":
                # For other binary data, include a reference
                user_message_parts.append(Part.from_text(f"[Binary content of type {part.get('mime_type', 'unknown')} was included]"))

    # Send the message to the model and get the response
    response = chat.send_message(user_message_parts, stream=True)

    # Process the streaming response
    for chunk in response:
        if chunk.text:
            yield chunk.text

