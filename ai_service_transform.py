"""
Module for transforming non-compliant documents using OpenAI.
This module provides functionality to transform non-compliant documents into compliant ones.
"""

import configuration
import base64
import requests
import os
import tempfile
import io
import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from data.country_data import COUNTRY_LANGUAGE_DESCRIPTION


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


def transform_document_with_openai(
    analysis_document: bytes, # This will always be a Text file
    non_compliant_document: bytes,
    file_type: str,
    country: str
) -> str:
    """
    Transform a non-compliant document into a compliant one using OpenAI.

    Args:
        document_data: The document data as bytes
        file_type: The MIME type of the document
        country: The country for which to ensure compliance

    Returns:
        Path to the transformed PDF document
    """
    # OpenAI API endpoint
    api_url = f"{configuration.OPENAI_API_BASE_URL}/chat/completions"

    # Prepare headers with an API key
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {configuration.OPENAI_API_KEY}"
    }

    # Process document data
    if file_type == "application/pdf":
        # For PDF, extract text and send it to OpenAI
        non_compliant_document_data = extract_text_from_pdf(non_compliant_document)
    elif file_type == "text/plain":
        # For text, we can decode and include it directly
        non_compliant_document_data = non_compliant_document.decode('utf-8', errors='replace')

    analysis_document_data = analysis_document

    language = COUNTRY_LANGUAGE_DESCRIPTION.get(country, "")
    # Create the system instruction and prompt
    system_instruction = f"You are a senior compliance officer for pharmaceutical regulations in {country}."

    user_instruction = f"""
    You will be provided with the following documents:
    1.  Analysis Document: {analysis_document_data}
    2.  Original Non Compliant Document: {non_compliant_document_data}

    Follow these steps to complete the task:

    1.  **Analyze the Analysis Document:** Carefully review the analysis document to identify all areas of non-compliance with official {country} medical norms.
    2.  **Reference the Original Non-Compliant Document:** Use the original non-compliant document as a reference to understand the context of each non-compliant item.
    3.  **Translate into {language}:** Translate the original non-compliant document into {language}. Ensure the translation is accurate and maintains the original meaning.
    4.  **Ensure Compliance:** While translating, ensure that all identified non-compliant items are corrected to fully comply with {country} medical norms. Use your expertise to make necessary adjustments and additions. Please also ensure that all the content of the non-compliant document is there and there should not be any loss of data until and unless it is non compliant data. Try to convert the non compliance data into compliant one and add it to the final compliant version.
    5.  **Generate Compliant PDF:** Create a final PDF version of the translated and compliant document. The PDF should be properly formatted and suitable for official use.
    6.  **Error Handling:** If full compliance cannot be achieved due to missing information or conflicting regulations, provide a detailed explanation of the issues and suggest possible resolutions.
    7.  **Language:** Ensure the final document is in {language} and adheres to professional language standards.

    Your output should be a fully compliant PDF document in {language}, adhering to all official {country} medical norms. 
    Please ensure that the document only consist of the translated and compliant content and no other information should be included.
    Especially some basis sytem information should not be included in the final document.
    """


    # Prepare messages for the API
    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": user_instruction}
    ]


    # Prepare the request data
    data = {
        "model": configuration.OPENAI_MODEL_NAME,
        "messages": messages,
        "temperature": 0.5,
        "max_tokens": 4000
    }

    # Make the API request
    response = requests.post(api_url, headers=headers, json=data)

    if response.status_code != 200:
        print(f"\nOpenAI API error: {response.status_code} - {response.text}\n")
        raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")


    # Extract the response content
    response_data = response.json()
    transformed_content = response_data['choices'][0]['message']['content']

    # Create a PDF with the transformed content
    return create_pdf_from_text(transformed_content)

def create_pdf_from_text(text: str) -> str:
    """
    Create a PDF file from a text.

    Args:
        text: The text to include in the PDF

    Returns:
        Path to the created PDF file
    """
    # Create a temporary file for the PDF
    fd, temp_path = tempfile.mkstemp(suffix='.pdf')
    os.close(fd)

    # Create the PDF
    doc = SimpleDocTemplate(temp_path, pagesize=letter)
    styles = getSampleStyleSheet()

    # Split the text into paragraphs
    paragraphs = text.split('\n\n')

    # Create a list of followable
    followable = []
    for para in paragraphs:
        if para.strip():
            p = Paragraph(para.replace('\n', '<br/>'), styles['Normal'])
            followable.append(p)
            followable.append(Spacer(1, 12))

    # Build the PDF
    doc.build(followable)

    return temp_path
