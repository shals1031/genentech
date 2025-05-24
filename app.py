from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
import os
import json
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_session import Session

# Import custom modules
from data.country_data import COUNTRY_LANGUAGE_DESCRIPTION
from processor import process_document, process_url, process_image, process_video
from processor.document import read_document_file
from ai_service_transform import transform_document_with_openai

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Configure a server-side session to prevent "cookie too large" warnings
# This moves session data from client-side cookies to server-side storage,
# which resolves issues with large session data exceeding the 4KB cookie size limit
app.config['SESSION_TYPE'] = 'filesystem'  # Store sessions in files
app.config['SESSION_FILE_DIR'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flask_session')
app.config['SESSION_PERMANENT'] = False  # Sessions expire when the browser closes
app.config['SESSION_USE_SIGNER'] = True  # Sign the session cookie for security
Session(app)  # Initialize the server-side session

# Create upload and session folders if they don't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if not os.path.exists(app.config['SESSION_FILE_DIR']):
    os.makedirs(app.config['SESSION_FILE_DIR'])


@app.route('/')
def index():
    """Render the main page with the first tab active."""
    return render_template('index.html',
                           countries=list(COUNTRY_LANGUAGE_DESCRIPTION.keys()),
                           content_types=["URL", "Document", "Image", "Video"],
                           active_tab="analyze")


@app.route('/analyze', methods=['POST'])
def analyze():
    """Process the content and analyze it."""
    # Get form data
    country = request.form.get('country')
    content_type = request.form.get('content_type')

    # Initialize variables
    file_path = None
    input_value = None
    file_type = None

    try:
        if content_type == "URL":
            input_value = request.form.get('input_value')
            # Process URL
            result_text = ""
            for chunk in process_url(url=input_value, country=country):
                result_text += chunk
        else:
            # Handle file upload
            if 'file' not in request.files:
                return jsonify({'error': 'No file part'}), 400

            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No selected file'}), 400

            # Create a unique filename
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)

            # Process file based on content type
            result_text = ""
            if content_type == "Document":
                for chunk in process_document(file_path=file_path, country=country):
                    result_text += chunk
                # Get a file type for later use
                _, file_type = read_document_file(file_path)
            elif content_type == "Image":
                for chunk in process_image(file_path=file_path, country=country):
                    result_text += chunk
            elif content_type == "Video":
                for chunk in process_video(file_path=file_path, country=country):
                    result_text += chunk

            input_value = file_path

        # Extract compliance status and other metrics from the result text
        json_data = extract_json_from_text(result_text)
        analysis_data = json.loads(json_data)

        # Determine compliance status
        compliance_status = analysis_data.get("Compliant Status", "Error: Compliance status not found.")
        is_compliant = analysis_data.get("Compliant Status", "").lower() == "compliant"
        analysis_result = analysis_data.get("Detailed Analysis", "Error: No analysis result found.")
        non_compliance_percentage = analysis_data.get("Non-Compliance Percentage", "0%")
        non_compliance_pages = analysis_data.get("Non-Compliant Pages", [])

        # Store data in session for use in other tabs
        session['analysis_result'] = analysis_result
        session['compliance_status'] = compliance_status
        session['is_compliant'] = is_compliant
        session['analysis_data'] = non_compliance_pages
        session['country'] = country
        session['content_type'] = content_type
        session['input_value'] = input_value
        session['file_type'] = file_type
        session['non_compliance_percentage'] = non_compliance_percentage

        # Read the original document content if it's a document
        if content_type == "Document" and file_path:
            document_data, file_type = read_document_file(file_path)
            # Set original_document for both text files and PDFs
            if file_type == "text/plain":
                session['original_document'] = document_data.decode('utf-8', errors='ignore')
            elif file_type == "application/pdf":
                # For PDF files, extract the text content
                from ai_service import extract_text_from_pdf
                pdf_text = extract_text_from_pdf(document_data)
                session['original_document'] = pdf_text
            else:
                # For other non-text files, don't try to display the raw content
                session['original_document'] = "Invalid file type. Only text files and PDFs are supported."

        # Redirect to the result tab
        return redirect(url_for('results'))

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/results')
def results():
    """Render the result tab."""
    if 'analysis_result' not in session:
        return redirect(url_for('index'))

    # Get original document content if available
    original_document = session.get('original_document', '')

    # Get the analysis data and sanitize the non-compliant sections
    analysis_data = session.get('analysis_data', {})

    # Process each non-compliant page to ensure all control characters are properly escaped
    if "Non-Compliant Pages" in analysis_data:
        for page in analysis_data["Non-Compliant Pages"]:
            if "Non-Compliant Text" in page:
                for text_item in page["Non-Compliant Text"]:
                    if "Text" in text_item:
                        # Replace any literal newlines with escaped newlines
                        text_item["Text"] = text_item["Text"].replace("\n", "\\n").replace("\r", "\\r")
                    if "Reason" in text_item:
                        text_item["Reason"] = text_item["Reason"].replace("\n", "\\n").replace("\r", "\\r")
    # For backward compatibility
    elif "Non-Compliant Sections" in analysis_data:
        for section in analysis_data["Non-Compliant Sections"]:
            if "Details" in section:
                # Replace any literal newlines with escaped newlines
                section["Details"] = section["Details"].replace("\n", "\\n").replace("\r", "\\r")
            if "Headline" in section:
                section["Headline"] = section["Headline"].replace("\n", "\\n").replace("\r", "\\r")

    # Sanitize Detailed Analysis if present
    if "Detailed Analysis" in analysis_data:
        analysis_data["Detailed Analysis"] = analysis_data["Detailed Analysis"].replace("\n", "\\n").replace("\r", "\\r")

    return render_template('results.html',
                           compliance_status=session['compliance_status'],
                           is_compliant= session['is_compliant'],
                           non_compliance_pages=session['analysis_data'],
                           non_compliance_percentage=session['non_compliance_percentage'],
                           analysis_result=session['analysis_result'],
                           original_document=original_document,
                           active_tab="results")


@app.route('/transform')
def transform():
    """Render the transform tab."""
    if 'analysis_result' not in session or session.get('is_compliant', True):
        return redirect(url_for('index'))

    return render_template('transform.html', active_tab="transform")


@app.route('/transform_document', methods=['POST'])
def transform_document():
    """Transform the document to make it compliant."""
    if 'analysis_result' not in session:
        return jsonify({'error': 'No analysis result found'}), 400

    try:
        # Get data from the session
        analysis_result = session['analysis_result']
        input_value = session['input_value']
        country = session['country']
        file_type = session['file_type']

        # Read the document file
        document_data, _ = read_document_file(input_value)

        # Transform the document
        transformed_pdf_path = transform_document_with_openai(
            analysis_result,
            document_data,
            file_type,
            country
        )

        # Create a unique filename for the transformed document
        base_filename = os.path.splitext(os.path.basename(input_value))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{base_filename}_transformed_{timestamp}.pdf"

        # Store the path in session for download
        session['transformed_pdf_path'] = transformed_pdf_path
        session['transformed_pdf_filename'] = output_filename

        return jsonify({'success': True, 'message': 'Document transformed successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download_transformed')
def download_transformed():
    """Download the transformed document."""
    if 'transformed_pdf_path' not in session:
        return redirect(url_for('index'))

    return send_file(
        session['transformed_pdf_path'],
        as_attachment=True,
        download_name=session['transformed_pdf_filename']
    )


def extract_json_from_text(text):
    """Extract JSON from text that might contain Markdown or other formatting."""
    if not text:
        return "{}"

    # Try to find JSON between triple backticks (Markdown code blocks)
    import re
    json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
    matches = re.findall(json_pattern, text)

    if matches:
        # Try each match until we find valid JSON
        for match in matches:
            try:
                # Validate that this is actually JSON
                json.loads(match.strip())
                return match.strip()
            except json.JSONDecodeError:
                continue

    # If no valid JSON found in code blocks, try to find JSON objects directly
    # Look for text that starts with { and ends with }
    json_pattern = r'(\{[\s\S]*?\})'
    matches = re.findall(json_pattern, text)

    if matches:
        # Sort matches by length (descending) to try the largest JSON objects first
        matches.sort(key=len, reverse=True)

        # Try each match until we find valid JSON
        for match in matches:
            try:
                # Validate that this is actually JSON
                json.loads(match.strip())
                return match.strip()
            except json.JSONDecodeError:
                continue

    # If we still haven't found valid JSON, try to create a basic JSON structure
    # Look for key patterns like "Compliant Status: X" and convert to JSON
    try:
        result = {}

        # Extract compliance status (the new format uses "Compliant Status")
        status_match = re.search(r'Compliant Status:?\s*([A-Za-z\s]+)', text, re.IGNORECASE)
        if status_match:
            result["Compliant Status"] = status_match.group(1).strip()
        else:
            # Try an old format as a fallback
            status_match = re.search(r'Compliance Status:?\s*([A-Za-z\s]+)', text, re.IGNORECASE)
            if status_match:
                result["Compliant Status"] = status_match.group(1).strip()

        # Extract percentage (a new format uses "Non-Compliance Percentage")
        percentage_match = re.search(r'Non-Compliance Percentage:?\s*(\d+(?:\.\d+)?)\s*%?', text, re.IGNORECASE)
        if percentage_match:
            result["Non-Compliance Percentage"] = percentage_match.group(1).strip() + "%"
        else:
            # Try an old format as a fallback
            percentage_match = re.search(r'Percentage of Non-Compliance:?\s*(\d+(?:\.\d+)?)\s*%?', text, re.IGNORECASE)
            if percentage_match:
                result["Non-Compliance Percentage"] = percentage_match.group(1).strip() + "%"

        # Extract detailed analysis
        detailed_analysis_match = re.search(r'Detailed Analysis:?\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\n(?=Non-Compliant Pages))', text, re.IGNORECASE)
        if detailed_analysis_match:
            result["Detailed Analysis"] = detailed_analysis_match.group(1).strip()

        # Extract non-compliant pages
        pages = []

        # Try to find page blocks
        page_blocks = re.finditer(
            r'Page Number:?\s*(\d+)(?:\s*Percentage of Non-Compliance:?\s*(\d+(?:\.\d+)?)\s*%?)?', 
            text, re.IGNORECASE
        )

        for page_match in page_blocks:
            page_number = page_match.group(1).strip()
            page_percentage = page_match.group(2).strip() + "%" if page_match.group(2) else "100%"

            # Find the start position of this page block
            start_pos = page_match.start()

            # Find the next page block or end of a text
            next_page_match = re.search(r'Page Number:?\s*\d+', text[start_pos + 1:], re.IGNORECASE)
            end_pos = start_pos + 1 + next_page_match.start() if next_page_match else len(text)

            # Extract the page block text
            page_block_text = text[start_pos:end_pos]

            # Extract non-compliant text items
            non_compliant_texts = []
            text_blocks = re.finditer(
                r'Text:?\s*([^\n]+)(?:\s*Reason:?\s*([^\n]+))?', 
                page_block_text, re.IGNORECASE
            )

            for text_match in text_blocks:
                text_item = {
                    "Text": text_match.group(1).strip() if text_match.group(1) else "",
                    "Reason": text_match.group(2).strip() if text_match.group(2) else "No reason provided"
                }
                non_compliant_texts.append(text_item)

            page = {
                "Page Number": page_number,
                "Percentage of Non-Compliance": page_percentage,
                "Non-Compliant Text": non_compliant_texts
            }
            pages.append(page)

        if pages:
            result["Non-Compliant Pages"] = pages
        else:
            # Fallback to old format if no pages found
            sections = []
            section_matches = re.finditer(
                r'Headline:?\s*([^\n]+)(?:\s*Details:?\s*([^\n]+))?(?:\s*Percentage:?\s*(\d+(?:\.\d+)?)\s*%?)?', text,
                re.IGNORECASE)

            for match in section_matches:
                section = {
                    "Headline": match.group(1).strip() if match.group(1) else "Unknown Section",
                    "Details": match.group(2).strip() if match.group(2) else "No details available",
                    "Percentage": match.group(3).strip() + "%" if match.group(3) else "0%"
                }
                sections.append(section)

            if sections:
                result["Non-Compliant Sections"] = sections
            else:
                result["Non-Compliant Pages"] = []

        # If we have at least some data, return the constructed JSON
        if len(result) > 0:
            return json.dumps(result)
    except Exception as e:
        print(f"Error parsing text: {str(e)}")
        pass

    # If all else fails, return a default JSON structure
    return json.dumps({
        "Compliant Status": "Unknown",
        "Non-Compliance Percentage": "0%",
        "Detailed Analysis": "No detailed analysis available.",
        "Non-Compliant Pages": []
    })


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
