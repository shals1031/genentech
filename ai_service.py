"""
Module for interacting with VertexAI services.
This module provides functionality to analyze content using VertexAI.
"""

import vertexai
import configuration
from typing import Iterator, Optional, Union, List

# Import VertexAI modules
from vertexai.generative_models import GenerativeModel, Part, Content, GenerationConfig
from vertexai.preview.generative_models import SafetySetting, HarmCategory, HarmBlockThreshold

# Initialize VertexAI
vertexai.init(project=configuration.PROJECT_ID, location=configuration.VERTEXT_AI_REGION_NAME)

def analyze_content(
    content_parts: List[Union[str, Part]],
    prompt: str = "Based on official medical norms in Switzerland, determine whether the content is compliant. If the content is not compliant, identify and highlight the specific parts of the document that violate the regulations.",
    system_instruction: str = "You are a senior compliance officer for pharmaceutical regulations in Switzerland. Your task is to analyze the provided content and determine whether it complies with official medical norms in Switzerland."
) -> Iterator[str]:
    """
    Analyze content using VertexAI.

    Args:
        content_parts: List of content parts to analyze (text or Part objects)
        prompt: The prompt to send to the model
        system_instruction: The system instruction for the model

    Returns:
        An iterator of response chunks from the model
    """
    # Create the model
    model = GenerativeModel(model_name=configuration.MODEL_NAME)

    # Create the safety settings
    safety_settings = [
        SafetySetting(
            category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=HarmBlockThreshold.BLOCK_NONE
        ),
        SafetySetting(
            category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=HarmBlockThreshold.BLOCK_NONE
        ),
        SafetySetting(
            category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            threshold=HarmBlockThreshold.BLOCK_NONE
        ),
        SafetySetting(
            category=HarmCategory.HARM_CATEGORY_HARASSMENT,
            threshold=HarmBlockThreshold.BLOCK_NONE
        )
    ]

    # Create the generation config
    generation_config = GenerationConfig(
        temperature=1.0,
        top_p=0.95,
        max_output_tokens=8192
    )

    # Create the user content with system instruction incorporated into the prompt
    combined_prompt = f"{system_instruction}\n\n{prompt}"

    # Prepare the parts list with the initial instruction
    parts = [Part.from_text("Analyze the following content:")]

    # Add all content parts
    for part in content_parts:
        if isinstance(part, str):
            parts.append(Part.from_text(part))
        else:
            parts.append(part)

    # Add the combined prompt at the end
    parts.append(Part.from_text(combined_prompt))

    # Create the user content
    user_content = Content(
        role="user",
        parts=parts
    )

    # Generate the content
    response = model.generate_content(
        contents=[user_content],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True
    )

    # Return the response chunks
    for chunk in response:
        if chunk.text:
            yield chunk.text
