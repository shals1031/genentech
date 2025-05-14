"""
Module for processing URLs using web scraping and VertexAI.
This module provides functionality to fetch content from URLs and analyze them using VertexAI.
"""

import requests
from typing import Iterator
from bs4 import BeautifulSoup
from vertexai.generative_models import Part

from ai_service import analyze_content_with_gemini

def fetch_url_content(url: str) -> str:
    """
    Fetch content from a URL and return it as a string.

    Args:
        url: URL to fetch content from

    Returns:
        The HTML content of the URL as a string
    """
    try:
        # Add http:// if not present
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        # Fetch the URL content
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract text content (remove scripts, styles, etc.)
        for script in soup(["script", "style"]):
            script.extract()

        # Get text content
        text = soup.get_text(separator='\n', strip=True)

        return text
    except Exception as e:
        raise Exception(f"Error fetching URL content: {str(e)}")

def process_url(
    url: str,
    country:str,
) -> Iterator[str]:
    """
    Process a URL using web scraping and VertexAI.

    Args:
        url: URL to process
        prompt: The prompt to send to the model
        system_instruction: The system instruction for the model

    Returns:
        An iterator of response chunks from the model
    """
    # Fetch the URL content
    url_content = fetch_url_content(url)

    # Create content parts for analysis
    content_parts = [
        f"URL: {url}",
        f"Content:\n{url_content}"
    ]

    # Analyze the content using VertexAI
    return analyze_content_with_gemini(
        content_parts=content_parts,
        country=country
    )
