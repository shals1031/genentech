# Pharma Compliance Tool

A sophisticated Flask web application for analyzing different types of content for compliance with pharmaceutical regulations across different countries.

## Features

- Country selection dropdown (Switzerland, Mexico, Brazil)
- Content type selection dropdown (URL, Document, Image, Video)
- Dynamic input field that changes based on content type:
  - URL: Text input for website URL
  - Document: File upload for PDF and TXT files
  - Image: File upload for JPEG, JPG, and PNG files
  - Video: File upload for MP4, WEBM, and MKV files
- Analysis results display with compliance status and detailed breakdown
- Non-compliant content transformation to make it compliant with regulations
- Download of transformed compliant documents

## Project Structure

```
genentech/
├── data/
│   ├── __init__.py
│   └── country_data.py       # Contains country to language code mapping
├── processor/
│   ├── __init__.py
│   ├── document.py           # Processes PDF and TXT files
│   ├── image.py              # Processes JPEG, JPG, PNG files
│   ├── url.py                # Processes web content
│   └── video.py              # Processes MP4, WEBM, MKV files
├── static/
│   └── css/
│       └── style.css         # Custom CSS styles
├── templates/
│   ├── base.html             # Base template with common layout
│   ├── index.html            # Main analysis page
│   ├── results.html          # Results display page
│   └── transform.html        # Document transformation page
├── uploads/                  # Directory for uploaded files
├── flask_session/            # Directory for server-side session storage
├── ai_service.py             # Integration with AI for content analysis
├── ai_service_transform.py   # AI service for transforming non-compliant content
├── app.py                    # Main Flask application
├── configuration.py          # Application configuration settings
├── requirements.txt          # Project dependencies
└── README.md                 # This file
```

## Requirements

- Python 3.6 or higher
- Flask: Web framework
- Flask-Session: For server-side session storage
- Werkzeug: WSGI utility library
- Requests: For fetching URL content
- BeautifulSoup4: For parsing HTML content
- AI services: For content analysis and transformation
- Other dependencies as specified in requirements.txt

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

To run the application, execute the following command from the project root:

```
python app.py
```

The application will be available at http://localhost:5000

## Usage

1. Select a country from the dropdown (Switzerland, Mexico, Brazil)
2. Select a content type from the dropdown (URL, Document, Image, Video)
3. Enter a URL or upload a file based on the content type:
   - URL: Enter a website URL
   - Document: Upload a PDF or TXT file
   - Image: Upload a JPEG, JPG, or PNG file
   - Video: Upload an MP4, WEBM, or MKV file
4. Click the "Analyze" button
5. View the compliance analysis results in the Results tab
6. If the content is non-compliant, use the Transform tab to make it compliant
7. Download the transformed compliant document

## Architecture

The application follows a modular design with clear separation of concerns:

- **data/country_data.py**: Contains language code mappings for supported countries
- **processor/**: Contains modules for processing different content types
- **templates/**: Contains HTML templates for the web interface
- **static/**: Contains static assets like CSS
- **ai_service.py**: Handles AI-powered content analysis
- **ai_service_transform.py**: Handles AI-powered content transformation
- **app.py**: Main Flask application that handles routing and business logic

## Server-Side Sessions

The application uses server-side sessions to store analysis results and other data. This prevents "cookie too large" warnings that can occur when storing large amounts of data in client-side cookies. Session data is stored in the `flask_session` directory.

## Content Analysis

Content is analyzed using AI services with customized prompts based on the selected country's regulations. The analysis determines whether the content complies with official medical norms and identifies specific non-compliant elements if present.

## Content Transformation

Non-compliant content can be transformed into compliant versions using AI services. The transformation process:
1. Analyzes the non-compliant sections
2. Applies country-specific medical norms
3. Rewrites content to ensure compliance while preserving meaning
4. Generates a new PDF document that meets all compliance requirements
