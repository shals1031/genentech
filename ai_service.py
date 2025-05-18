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
              You will be provided with the following document

              Follow these steps to determine compliance:

              1.  Analyze the document content been provided .
              2.  Determine whether the content is compliant with these official medical norms in {country}.
              3.  If the content is not compliant:
                *   Identify and highlight the specific parts of the document that violate the regulations.
                *   Calculate the percentage of the document that is non-compliant for each section.
              4.  Present your analysis, clearly indicating whether the document is compliant or non-compliant, 
                  the specific violations (if any), and the percentage of non-compliance for each section and overall document.
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

def format_analysis_document_with_gemini(
        analysis_document: str, # This will always be a Text file
        country:str
) -> Iterator[str]:
    """
        Analyze content using VertexAI (Gemini).

        Args:
            analysis_document: Binary data of the text file to analyze
            country: The country for which to check compliance

        Returns:
            An iterator of response chunks from the model
        """
    # Initialize the Gemini model
    model = GenerativeModel(configuration.MODEL_NAME)

    # Create a chat session
    chat = model.start_chat()

    system_instruction = f"""
                    You are a senior compliance officer for pharmaceutical regulations in {country}. 
                    Your task is to analyze a document and extract key metrics related to compliance with medical norms. 
                    """

    prompt = f"""
                You will be provided with the document:
                Follow these steps to analyze the document and extract the required metrics:

                3. Create a list of objects, each representing a non-compliant section. Each object should have the following attributes:
                    Headline: The headline of the non-compliant section.
                    Details: Specific details of the non-compliant aspects in that section.
                    Percentage: The percentage of non-compliance within that specific section.

                Output the results in the following order in a valid JSON beautify format:

                1. Compliance Status: [COMPLIANT/NOT COMPLIANT]
                2. Percentage of Non-Compliance: [Percentage]%
                3. Non-Compliant Sections:
                    Headline: [Headline of the section]
                    Details: [Details of the non-compliant aspects]
                    Percentage: [Percentage of non-compliance in this section]%
                  """

    # Convert analysis_document bytes to text
    document_text = analysis_document

    # Create the user message with system instruction, prompt and document content
    user_message_parts = [
        Part.from_text(f"System instruction: {system_instruction}\n\nAnalyze the following document:\n\n{prompt}\n\nDocument content:\n\n{document_text}")
    ]

    # Send the message to the model and get the response
    response = chat.send_message(user_message_parts, stream=True)

    # Process the streaming response
    for chunk in response:
        if chunk.text:
            yield chunk.text
