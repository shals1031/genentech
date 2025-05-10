"""
Module for processing video files (MP4, WEBM, MKV) using VertexAI.
This module provides functionality to read video files and analyze them using VertexAI.
"""

import os
from typing import Iterator
from vertexai.generative_models import Part

from ai_service import analyze_content

def read_video_file(file_path: str) -> tuple[bytes, str]:
    """
    Read a video file (MP4, WEBM, MKV) and return its contents as bytes and the file type.

    Args:
        file_path: Path to the video file

    Returns:
        A tuple containing the contents of the video file as bytes and the file type
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    file_extension = os.path.splitext(file_path)[1].lower()

    with open(file_path, "rb") as file:
        file_data = file.read()

    if file_extension == '.mp4':
        file_type = "video/mp4"
    elif file_extension == '.webm':
        file_type = "video/webm"
    elif file_extension == '.mkv':
        file_type = "video/x-matroska"
    else:
        raise ValueError(f"Unsupported file type: {file_extension}. Only MP4, WEBM, and MKV files are supported.")

    return file_data, file_type

def process_video(
    file_path: str,
    prompt = "Based on official medical norms in Switzerland, determine whether the content is compliant. If the content is not compliant, identify and highlight the specific parts of the video that violate the regulations.",
    system_instruction: str = "You are a senior compliance officer for pharmaceutical regulations in Switzerland. Your task is to analyze the provided video and determine whether it complies with official medical norms in Switzerland."
) -> Iterator[str]:
    """
    Process a video file (MP4, WEBM, MKV) using VertexAI.

    Args:
        file_path: Path to the video file
        prompt: The prompt to send to the model
        system_instruction: The system instruction for the model

    Returns:
        An iterator of response chunks from the model
    """
    # Read the video file
    video_data, file_type = read_video_file(file_path)

    # Create content parts for analysis
    content_parts = [
        Part.from_data(video_data, file_type)
    ]

    # Analyze the content using VertexAI
    return analyze_content(
        content_parts=content_parts,
        prompt=prompt,
        system_instruction=system_instruction
    )
