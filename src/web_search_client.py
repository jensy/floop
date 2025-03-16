"""
Web Search Client Module

This module provides functions to interact with OpenAI's web search API.
"""

import os
import logging
import time
from typing import Dict, List, Optional, Union, Any
import openai
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
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_web_search(
    query: Union[str, Dict[str, Any]],
    max_retries: int = 3,
    retry_delay: float = 1.0
) -> Dict[str, Any]:
    """
    Perform a web search using OpenAI's web search capability.
    
    Args:
        query: The search query or a dictionary containing the query
        max_retries: Maximum number of retries for temporary failures
        retry_delay: Delay between retries in seconds
        
    Returns:
        Dictionary containing the search results and metadata
    """
    # Extract the query from input
    if isinstance(query, dict):
        search_query = query.get("text", "")
        source = query.get("source", "unknown")
    else:
        search_query = query
        source = "direct"
    
    if not search_query:
        logger.error("Empty search query")
        return {"error": "Empty search query", "text": "Error: Empty search query"}
    
    retry_count = 0
    
    while retry_count <= max_retries:
        try:
            logger.info(f"Performing web search for query: {search_query}")
            
            # Use OpenAI's GPT model with web search capability
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant with access to web search. When answering, always cite your sources with URLs."},
                    {"role": "user", "content": f"Search the web for information about: {search_query}"}
                ]
            )
            
            # Extract the response text
            response_text = response.choices[0].message.content
            
            logger.info("Successfully received response from web search")
            
            # Return a dictionary with the response and metadata
            return {
                "text": response_text,
                "query": search_query,
                "source": source,
                "model": "web_search",
                "usage": {
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens
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
                logger.error(f"Error calling web search API: {error_message}")
                return {
                    "error": error_message,
                    "text": f"Error performing web search: {error_message}"
                }
    
    # This should not be reached, but just in case
    return {
        "error": "Maximum retries exceeded",
        "text": "Error performing web search: Maximum retries exceeded"
    }

def format_search_results(search_results: Dict[str, Any]) -> str:
    """
    Format search results into a readable text format.
    
    Args:
        search_results: Dictionary containing search results
        
    Returns:
        Formatted search results as a string
    """
    if "error" in search_results:
        return f"Error performing web search: {search_results['error']}"
    
    # Return the response text directly
    return search_results.get("text", "No search results found.")

# Simple test function
def test_web_search():
    """Test the web search API with a simple query."""
    response = call_web_search("Latest AI breakthroughs")
    if "error" in response:
        print(f"Error: {response['error']}")
    else:
        print(format_search_results(response))
    return response

if __name__ == "__main__":
    # Run the test function if this file is executed directly
    test_web_search() 