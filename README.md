# Content Processor Application

A Tkinter-based GUI application for processing different types of content based on country and content type selections.

## Features

- Country selection dropdown (Switzerland, Mexico, Brazil)
- Content type selection dropdown (URL, Document, Image, Video)
- Dynamic input field that changes based on content type:
  - URL: Simple text input
  - Document, Image, Video: Text input with browse button
- Process button to submit the form
- Output text area to display results

## Project Structure

```
content-processor/
├── data/
│   ├── __init__.py
│   └── country_data.py  # Contains country to language code mapping
├── ui/
│   ├── __init__.py
│   └── components.py    # Reusable UI components
├── main.py              # Main application entry point
└── README.md            # This file
```

## Requirements

- Python 3.6 or higher
- Tkinter (usually comes with Python installation)

## Running the Application

To run the application, execute the following command from the project root:

```bash
python main.py
```

## Code Structure

The application follows a modular design with separation of concerns:

- **data/country_data.py**: Contains the data model with country to language code mapping
- **ui/components.py**: Contains reusable UI components (LabeledCombobox, InputField, TextArea)
- **main.py**: Main application that connects all components and implements the application logic

## Usage

1. Select a country from the dropdown
2. Select a content type from the dropdown
3. Enter a URL or select a file depending on the content type
4. Click the "Process" button
5. View the results in the output text area
