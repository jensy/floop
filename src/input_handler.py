"""
Input Handler Module

This module provides functions to handle input from CLI and files.
"""

import os
import logging
from typing import Optional, Dict, Any
import click

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_text_input(prompt: str = "Enter your prompt: ") -> str:
    """
    Get text input from the user via CLI.
    
    Args:
        prompt: The prompt to display to the user
        
    Returns:
        The user's input text
    """
    try:
        user_input = input(prompt)
        if not user_input.strip():
            logger.warning("Empty input provided")
            return ""
        return user_input
    except Exception as e:
        logger.error(f"Error getting text input: {str(e)}")
        return ""

def read_file(file_path: str) -> Optional[str]:
    """
    Read content from a file.
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        The file content as a string, or None if an error occurred
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None
            
        # Check if file is readable
        if not os.path.isfile(file_path):
            logger.error(f"Not a file: {file_path}")
            return None
            
        # Read file content
        logger.info(f"Reading file: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Check if file is empty
        if not content.strip():
            logger.warning(f"File is empty: {file_path}")
            return ""
            
        logger.info(f"Successfully read file: {file_path} ({len(content)} characters)")
        return content
        
    except Exception as e:
        logger.error(f"Error reading file: {str(e)}")
        return None

def process_input(input_text: Optional[str] = None, input_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Process input from either text or file.
    
    Args:
        input_text: Direct text input
        input_file: Path to input file
        
    Returns:
        Dictionary containing the processed input and metadata
    """
    # Check if both inputs are None
    if input_text is None and input_file is None:
        logger.error("No input provided")
        return {"error": "No input provided", "text": None}
        
    # Process file input if provided
    if input_file is not None:
        content = read_file(input_file)
        if content is None:
            return {"error": f"Failed to read file: {input_file}", "text": None}
        return {"text": content, "source": "file", "file_path": input_file}
        
    # Process text input
    if not input_text.strip():
        return {"error": "Empty input provided", "text": None}
        
    return {"text": input_text, "source": "text"}

# CLI interface using Click
@click.command()
@click.option('--input', '-i', help='Direct text input')
@click.option('--input_file', '-f', help='Path to input file')
def cli(input: Optional[str] = None, input_file: Optional[str] = None):
    """Process input from text or file and print the result."""
    # If no input is provided, prompt the user
    if input is None and input_file is None:
        input = get_text_input()
        
    result = process_input(input, input_file)
    
    if "error" in result:
        click.echo(f"Error: {result['error']}")
    else:
        click.echo(f"Input processed successfully!")
        click.echo(f"Source: {result['source']}")
        if result['source'] == 'file':
            click.echo(f"File: {result['file_path']}")
        click.echo(f"Content: {result['text'][:100]}..." if len(result['text']) > 100 else f"Content: {result['text']}")

if __name__ == "__main__":
    # Run the CLI if this file is executed directly
    cli() 