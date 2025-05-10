# Pharma Compliance Tool

A sophisticated Tkinter-based GUI application for analyzing different types of content for compliance with pharmaceutical regulations across different countries.

## Features

- Country selection dropdown (Switzerland, Mexico, Brazil)
- Content type selection dropdown (URL, Document, Image, Video)
- Dynamic input field that changes based on content type:
  - URL: Text input for website URL
  - Document: Text input with browse button for PDF and TXT files
  - Image: Text input with browse button for JPEG, JPG, and PNG files
  - Video: Text input with browse button for MP4, WEBM, and MKV files
- Process button to submit content for analysis
- Output text area displaying compliance results
- Automatic generation and saving of detailed compliance reports as Word documents

## Project Structure

genentech/ ├── data/ │ ├── **init**.py │ └── country_data.py # Contains country to language code mapping ├── processor/ │ ├── **init**.py │ ├── document.py # Processes PDF and TXT files │ ├── image.py # Processes JPEG, JPG, PNG files │ ├── url.py # Processes web content │ └── video.py # Processes MP4, WEBM, MKV files ├── ui/ │ ├── **init**.py │ ├── input_field.py # Input field component with browse functionality │ ├── labeled_combobox.py # Labeled dropdown component │ └── text_area.py # Text area for displaying results ├── ai_service.py # Integration with VertexAI for content analysis ├── configuration.py # Application configuration settings ├── main.py # Main application entry point └── README.md # This file

## Requirements

- Python 3.6 or higher
- Tkinter (usually comes with Python installation)
- python-docx: For creating Word documents
- requests: For fetching URL content
- BeautifulSoup4: For parsing HTML content
- vertexai: For AI-powered content analysis
- Other dependencies as specified in the code

## Running the Application

To run the application, execute the following command from the project root:

## Usage

1. Select a country from the dropdown (Switzerland, Mexico, Brazil)
2. Select a content type from the dropdown (URL, Document, Image, Video)
3. Enter a URL or select a file based on the content type:
   - URL: Enter a website URL (http:// will be automatically added if missing)
   - Document: Browse and select a PDF or TXT file
   - Image: Browse and select a JPEG, JPG, or PNG file
   - Video: Browse and select an MP4, WEBM, or MKV file
4. Click the "Process" button
5. View the compliance analysis results in the output text area
6. Save the detailed compliance report as a Word document

## Architecture

The application follows a modular design with clear separation of concerns:

- **data/country_data.py**: Contains language code mappings for supported countries
- **processor/**: Contains modules for processing different content types using VertexAI
- **ui/**: Contains reusable UI components for the application interface
- **ai_service.py**: Handles communication with VertexAI for content analysis
- **main.py**: Main application that orchestrates UI components and processing logic

## Content Analysis

Content is analyzed using VertexAI with customized prompts based on the selected country's regulations. The analysis determines whether the content complies with official medical norms and identifies specific non-compliant elements if present.

## Report Generation

After analysis, the application generates a detailed Word document containing:
- Content identification information
- Analysis date and time
- Compliance status summary
- Detailed analysis results from VertexAI

This document can be saved to a location of the user's choice with a timestamp-based filename.