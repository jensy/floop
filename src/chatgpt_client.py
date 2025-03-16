"""
ChatGPT Client Module

This module provides functions to interact with OpenAI's ChatGPT API.
"""

import os
import logging
import time
from typing import Dict, List, Optional, Union, Any
from openai import OpenAI
from openai.types.chat import ChatCompletion
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_chatgpt(
    input_data: Union[str, Dict[str, Any]],
    model: str = "gpt-3.5-turbo",
    max_tokens: int = 1000,
    temperature: float = 0.7,
    max_retries: int = 3,
    retry_delay: float = 1.0
) -> Dict[str, Any]:
    """
    Send a request to OpenAI's ChatGPT API and return the response.
    
    Args:
        input_data: The user's input text or a dictionary containing input data
        model: The OpenAI model to use (default: gpt-3.5-turbo)
        max_tokens: Maximum number of tokens in the response
        temperature: Controls randomness (0-1)
        max_retries: Maximum number of retries for temporary failures
        retry_delay: Delay between retries in seconds
        
    Returns:
        Dictionary containing the response text and metadata
    """
    # Extract the prompt from input_data
    if isinstance(input_data, dict):
        prompt = input_data.get("text", "")
        source = input_data.get("source", "unknown")
        
        # Handle directory input
        if source == "directory":
            # If we have individual file results, process each one
            if "files" in input_data and input_data.get("processing_strategy") == "individual":
                results = []
                for file_info in input_data["files"]:
                    file_path = file_info.get("file_path", "unknown")
                    content = file_info.get("content", "")
                    
                    logger.info(f"Processing file: {file_path}")
                    file_result = call_chatgpt_single(content, model, max_tokens, temperature, max_retries, retry_delay)
                    
                    # Add file path to result
                    file_result["file_path"] = file_path
                    results.append(file_result)
                
                # Return combined results
                return {
                    "results": results,
                    "model": model,
                    "input_source": "directory",
                    "directory_path": input_data.get("directory_path", "unknown"),
                    "file_count": len(results),
                    "processing_strategy": "individual",
                    "metadata": {
                        "successful_files": sum(1 for r in results if "error" not in r),
                        "failed_files": sum(1 for r in results if "error" in r)
                    }
                }
    else:
        prompt = input_data
    
    # Call ChatGPT with the prompt
    return call_chatgpt_single(prompt, model, max_tokens, temperature, max_retries, retry_delay)

def call_chatgpt_single(
    prompt: str,
    model: str = "gpt-3.5-turbo",
    max_tokens: int = 1000,
    temperature: float = 0.7,
    max_retries: int = 3,
    retry_delay: float = 1.0
) -> Dict[str, Any]:
    """
    Send a single request to OpenAI's ChatGPT API and return the response.
    
    Args:
        prompt: The user's input text
        model: The OpenAI model to use (default: gpt-3.5-turbo)
        max_tokens: Maximum number of tokens in the response
        temperature: Controls randomness (0-1)
        max_retries: Maximum number of retries for temporary failures
        retry_delay: Delay between retries in seconds
        
    Returns:
        Dictionary containing the response text and metadata
    """
    retry_count = 0
    
    while retry_count <= max_retries:
        try:
            logger.info(f"Calling ChatGPT with model: {model}")
            
            # Create the messages list with a system and user message
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
            
            # Call the OpenAI API
            response: ChatCompletion = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Extract the response text
            response_text = response.choices[0].message.content
            
            logger.info("Successfully received response from ChatGPT")
            
            # Return a dictionary with the response text and metadata
            return {
                "text": response_text,
                "model": model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
        except Exception as e:
            retry_count += 1
            error_message = str(e)
            
            # Check if the error is temporary (e.g., rate limit, timeout)
            is_temporary_error = any(
                error_type in error_message.lower()
                for error_type in ["timeout", "rate limit", "server error", "503", "429"]
            )
            
            if is_temporary_error and retry_count <= max_retries:
                # Calculate exponential backoff delay
                delay = retry_delay * (2 ** (retry_count - 1))
                logger.warning(f"Temporary error: {error_message}. Retrying in {delay:.2f} seconds (attempt {retry_count}/{max_retries})...")
                time.sleep(delay)
            else:
                # Permanent error or max retries reached
                logger.error(f"Error calling ChatGPT API: {error_message}")
                return {
                    "error": error_message,
                    "text": "Sorry, I encountered an error while processing your request."
                }
    
    # This should not be reached, but just in case
    return {
        "error": "Maximum retries exceeded",
        "text": "Sorry, I encountered an error while processing your request."
    }

# Simple test function
def test_chatgpt():
    """Test the ChatGPT API with a simple prompt."""
    response = call_chatgpt("Hello, how are you?")
    if "error" in response:
        print(f"Error: {response['error']}")
    else:
        print(f"ChatGPT says: {response['text']}")
        print(f"Token usage: {response['usage']}")
    return response

if __name__ == "__main__":
    # Run the test function if this file is executed directly
    test_chatgpt() 