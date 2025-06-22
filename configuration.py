import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Add your VertextAI details here
PROJECT_ID = "poc-projects-462113"
VERTEXT_AI_REGION_NAME = "us-central1"
MODEL_NAME = "gemini-2.5-pro"
# Add your OpenAI API details here
OPENAI_API_BASE_URL = "https://api.openai.com/v1"
OPENAI_MODEL_NAME = "gpt-4.1"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")  # Get API key from environment