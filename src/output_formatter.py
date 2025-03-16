"""
Output Formatter Module

This module provides functions to format and clean output from AI models.
"""

import re
import os
import logging
import json
from typing import Dict, Any, Optional, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """
    Clean and format text by removing unnecessary whitespace and fixing formatting issues.
    
    Args:
        text: The text to clean
        
    Returns:
        The cleaned text
    """
    if not text:
        return ""
        
    # Remove excessive whitespace
    cleaned = re.sub(r'\s+', ' ', text)
    
    # Fix common formatting issues
    cleaned = cleaned.strip()
    
    # Ensure proper sentence endings
    if cleaned and not cleaned.endswith(('.', '!', '?', ':', ';')):
        cleaned += '.'
        
    logger.debug(f"Cleaned text (length: {len(cleaned)})")
    return cleaned

def format_output(response: Dict[str, Any], include_metadata: bool = True) -> Dict[str, Any]:
    """
    Format the output from an AI model.
    
    Args:
        response: The response from the AI model
        include_metadata: Whether to include metadata in the output
        
    Returns:
        The formatted output
    """
    if not response:
        logger.warning("Invalid response format")
        return response
        
    # Check if this is a directory result with multiple files
    if "results" in response:
        # Format each individual result
        for i, file_result in enumerate(response["results"]):
            if "text" in file_result:
                file_result["text"] = clean_text(file_result["text"])
                
        logger.info(f"Formatted {len(response['results'])} file results")
        return response
    
    # Single result processing
    if "text" in response:
        response["text"] = clean_text(response["text"])
        
    # Format metadata if included
    if include_metadata and "metadata" in response:
        # Keep metadata as is for now
        pass
        
    logger.info("Output formatted successfully")
    return response

def format_for_display(response: Dict[str, Any], format_type: str = "text") -> str:
    """
    Format the response for display in the specified format.
    
    Args:
        response: The response from the AI model
        format_type: The format to use (text, markdown, json, html)
        
    Returns:
        The formatted output as a string
    """
    if not response:
        return "No response available."
        
    if "error" in response:
        return f"Error: {response['error']}"
    
    # Check if this is a directory result with multiple files
    if "results" in response:
        return format_directory_results(response, format_type)
    
    # Get the response text
    response_text = response.get("text", "")
    
    if format_type == "text":
        # Simple text format
        output = response_text
    elif format_type == "markdown":
        # Markdown format with metadata
        model_info = response.get("model", "unknown")
        output = f"# AI Response\n\n{response_text}\n\n*Generated by {model_info}*"
    elif format_type == "json":
        # JSON format
        output = json.dumps(response, indent=2)
    elif format_type == "html":
        # HTML format
        model_info = response.get("model", "unknown")
        html_response = response_text.replace('\n', '<br>')
        
        output = '<!DOCTYPE html>\n'
        output += '<html>\n'
        output += '<head>\n'
        output += '    <title>AI Response</title>\n'
        output += '    <style>\n'
        output += '        body { font-family: Arial, sans-serif; margin: 20px; }\n'
        output += '        h1 { color: #333; }\n'
        output += '        .response { padding: 10px; background-color: #f9f9f9; border-radius: 5px; }\n'
        output += '        .metadata { font-style: italic; color: #666; }\n'
        output += '    </style>\n'
        output += '</head>\n'
        output += '<body>\n'
        output += '    <h1>AI Response</h1>\n'
        output += f'    <div class="response">{html_response}</div>\n'
        output += f'    <p class="metadata">Generated by {model_info}</p>\n'
        output += '</body>\n'
        output += '</html>'
    else:
        # Default to simple text
        output = response_text
        
    logger.info(f"Output formatted for display ({format_type})")
    return output

def format_directory_results(response: Dict[str, Any], format_type: str = "markdown") -> str:
    """
    Format the results from processing multiple files in a directory.
    
    Args:
        response: The response containing results from processing files
        format_type: The format to use (text, markdown, json, html)
        
    Returns:
        The formatted output as a string
    """
    results = response.get("results", [])
    if not results:
        return "No results available."
    
    # Count successful and failed files
    successful = response.get("metadata", {}).get("successful_files", 0)
    failed = response.get("metadata", {}).get("failed_files", 0)
    directory_path = response.get("directory_path", "unknown")
    model = response.get("model", "unknown")
    
    if format_type == "text":
        # Simple text format
        output = f"Directory Processing Results\n"
        output += f"Directory: {directory_path}\n"
        output += f"Files Processed: {len(results)}\n"
        output += f"Successful: {successful}\n"
        output += f"Failed: {failed}\n"
        output += f"Model: {model}\n\n"
        
        # Add each file result
        for i, file_result in enumerate(results, 1):
            file_path = file_result.get("file_path", "Unknown file")
            output += f"{i}. {os.path.basename(file_path)}\n"
            output += f"Path: {file_path}\n"
            
            if "error" in file_result:
                output += f"Error: {file_result['error']}\n\n"
            else:
                output += f"Result: {file_result.get('text', '')}\n\n"
                
    elif format_type == "markdown":
        # Create a markdown report
        output = f"# Directory Processing Results\n\n"
        output += f"**Directory:** {directory_path}\n"
        output += f"**Files Processed:** {len(results)}\n"
        output += f"**Successful:** {successful}\n"
        output += f"**Failed:** {failed}\n"
        output += f"**Model:** {model}\n\n"
        
        # Add each file result
        for i, file_result in enumerate(results, 1):
            file_path = file_result.get("file_path", "Unknown file")
            output += f"## {i}. {os.path.basename(file_path)}\n\n"
            output += f"**Path:** {file_path}\n\n"
            
            if "error" in file_result:
                output += f"**Error:** {file_result['error']}\n\n"
            else:
                output += f"**Result:**\n\n{file_result.get('text', '')}\n\n"
                
            output += "---\n\n"
            
    elif format_type == "json":
        # JSON format
        output = json.dumps(response, indent=2)
        
    elif format_type == "html":
        # HTML format
        output = '<!DOCTYPE html>\n'
        output += '<html>\n'
        output += '<head>\n'
        output += '    <title>Directory Processing Results</title>\n'
        output += '    <style>\n'
        output += '        body { font-family: Arial, sans-serif; margin: 20px; }\n'
        output += '        h1, h2 { color: #333; }\n'
        output += '        .summary { padding: 10px; background-color: #f0f0f0; border-radius: 5px; margin-bottom: 20px; }\n'
        output += '        .file-result { padding: 10px; background-color: #f9f9f9; border-radius: 5px; margin-bottom: 15px; }\n'
        output += '        .file-path { color: #666; font-style: italic; }\n'
        output += '        .error { color: #cc0000; }\n'
        output += '    </style>\n'
        output += '</head>\n'
        output += '<body>\n'
        output += '    <h1>Directory Processing Results</h1>\n'
        output += '    <div class="summary">\n'
        output += f'        <p><strong>Directory:</strong> {directory_path}</p>\n'
        output += f'        <p><strong>Files Processed:</strong> {len(results)}</p>\n'
        output += f'        <p><strong>Successful:</strong> {successful}</p>\n'
        output += f'        <p><strong>Failed:</strong> {failed}</p>\n'
        output += f'        <p><strong>Model:</strong> {model}</p>\n'
        output += '    </div>\n'
        
        # Add each file result
        for i, file_result in enumerate(results, 1):
            file_path = file_result.get("file_path", "Unknown file")
            output += '    <div class="file-result">\n'
            output += f'        <h2>{i}. {os.path.basename(file_path)}</h2>\n'
            output += f'        <p class="file-path">Path: {file_path}</p>\n'
            
            if "error" in file_result:
                output += f'        <p class="error">Error: {file_result["error"]}</p>\n'
            else:
                output += '        <p><strong>Result:</strong></p>\n'
                result_text = file_result.get('text', '').replace('\n', '<br>')
                output += f'        <div>{result_text}</div>\n'
                
            output += '    </div>\n'
            
        output += '</body>\n'
        output += '</html>'
    else:
        # Default to simple text
        output = f"Directory Processing Results\n"
        output += f"Files Processed: {len(results)}\n"
        output += f"Successful: {successful}\n"
        output += f"Failed: {failed}\n\n"
        
    logger.info(f"Directory results formatted for display ({format_type})")
    return output

def save_results_to_file(response: Dict[str, Any], output_file: str, 
                        format_type: str = "markdown") -> bool:
    """
    Save the results to a file.
    
    Args:
        response: The response from the AI model
        output_file: The file path to write the results to
        format_type: The format to use (text, markdown, json)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        
        # Check if this is a directory result with multiple files
        if "results" in response:
            if format_type == "json":
                # Save as JSON
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(response, f, indent=2)
            else:
                # Format and save as text or markdown
                formatted = format_directory_results(response, format_type)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(formatted)
        else:
            # Single result
            if format_type == "json":
                # Save as JSON
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(response, f, indent=2)
            else:
                # Format and save as text or markdown
                formatted = format_for_display(response, format_type)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(formatted)
                    
        logger.info(f"Results saved to {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving results to file: {str(e)}")
        return False 