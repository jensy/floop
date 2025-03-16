"""
Input Handler Module

This module provides functions to handle input from CLI, files, and directories.
"""

import os
import sys
import glob
import logging
from typing import Optional, Dict, Any, List
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

def find_files_in_directory(directory_path: str, file_pattern: str = "*.txt", recursive: bool = False) -> List[str]:
    """
    Find files in a directory matching a pattern.
    
    Args:
        directory_path: Path to the directory
        file_pattern: Glob pattern for files to match (default: "*.txt")
        recursive: Whether to search recursively in subdirectories (default: False)
        
    Returns:
        List of file paths matching the pattern
    """
    try:
        if not os.path.exists(directory_path):
            logger.error(f"Directory not found: {directory_path}")
            return []
            
        if not os.path.isdir(directory_path):
            logger.error(f"Not a directory: {directory_path}")
            return []
            
        # Construct the search pattern
        if recursive:
            search_pattern = os.path.join(directory_path, "**", file_pattern)
            files = glob.glob(search_pattern, recursive=True)
        else:
            search_pattern = os.path.join(directory_path, file_pattern)
            files = glob.glob(search_pattern)
            
        logger.info(f"Found {len(files)} files matching pattern '{file_pattern}' in {directory_path}")
        return sorted(files)
        
    except Exception as e:
        logger.error(f"Error finding files in directory: {str(e)}")
        return []

def process_directory(directory_path: str, file_pattern: str = "*.txt", 
                     recursive: bool = False, processing_strategy: str = "individual") -> Dict[str, Any]:
    """
    Process files in a directory according to a strategy.
    
    Args:
        directory_path: Path to the directory
        file_pattern: Glob pattern for files to match (default: "*.txt")
        recursive: Whether to search recursively in subdirectories (default: False)
        processing_strategy: How to process the files - "individual" or "concatenate" (default: "individual")
        
    Returns:
        Dictionary containing the processed input and metadata
    """
    files = find_files_in_directory(directory_path, file_pattern, recursive)
    
    if not files:
        return {"error": f"No files found matching pattern '{file_pattern}' in {directory_path}", "text": None}
        
    if processing_strategy == "concatenate":
        # Concatenate all file contents into a single string
        all_content = []
        file_paths = []
        
        for file_path in files:
            content = read_file(file_path)
            if content is not None:
                all_content.append(content)
                file_paths.append(file_path)
                
        if not all_content:
            return {"error": "Failed to read any files in the directory", "text": None}
            
        combined_content = "\n\n--- Next File ---\n\n".join(all_content)
        return {
            "text": combined_content, 
            "source": "directory", 
            "directory_path": directory_path,
            "file_count": len(file_paths),
            "files": file_paths,
            "processing_strategy": "concatenate"
        }
    elif processing_strategy == "individual":
        # Return a list of individual file contents
        file_contents = []
        
        for file_path in files:
            content = read_file(file_path)
            if content is not None:
                file_contents.append({
                    "file_path": file_path,
                    "content": content
                })
                
        if not file_contents:
            return {"error": "Failed to read any files in the directory", "text": None}
            
        return {
            "files": file_contents,
            "source": "directory",
            "directory_path": directory_path,
            "file_count": len(file_contents),
            "processing_strategy": "individual"
        }
    else:
        return {"error": f"Unknown processing strategy: {processing_strategy}", "text": None}

def process_input(input_text: Optional[str] = None, input_file: Optional[str] = None, 
                 input_directory: Optional[str] = None, file_pattern: str = "*.txt",
                 recursive: bool = False, processing_strategy: str = "individual") -> Dict[str, Any]:
    """
    Process input from text, file, or directory.
    
    Args:
        input_text: Direct text input
        input_file: Path to input file
        input_directory: Path to input directory
        file_pattern: Glob pattern for files to match when using directory input
        recursive: Whether to search recursively in subdirectories
        processing_strategy: How to process directory files - "individual" or "concatenate"
        
    Returns:
        Dictionary containing the processed input and metadata
    """
    # Check input priority: directory > file > text
    if input_directory is not None:
        return process_directory(input_directory, file_pattern, recursive, processing_strategy)
        
    # Check if both text and file inputs are None
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
@click.option('--input_directory', '-d', help='Path to input directory')
@click.option('--file_pattern', default="*.txt", help='File pattern for directory input (default: *.txt)')
@click.option('--recursive', is_flag=True, help='Search recursively in subdirectories')
@click.option('--processing_strategy', type=click.Choice(['individual', 'concatenate']), 
              default='individual', help='How to process directory files')
def cli(input: Optional[str] = None, input_file: Optional[str] = None, 
        input_directory: Optional[str] = None, file_pattern: str = "*.txt",
        recursive: bool = False, processing_strategy: str = "individual"):
    """Process input from text, file, or directory and print the result."""
    # If no input is provided, prompt the user
    if input is None and input_file is None and input_directory is None:
        input = get_text_input()
        
    result = process_input(input, input_file, input_directory, file_pattern, recursive, processing_strategy)
    
    if "error" in result:
        click.echo(f"Error: {result['error']}")
    else:
        click.echo(f"Input processed successfully!")
        click.echo(f"Source: {result['source']}")
        
        if result['source'] == 'file':
            click.echo(f"File: {result['file_path']}")
            click.echo(f"Content: {result['text'][:100]}..." if len(result['text']) > 100 else f"Content: {result['text']}")
        elif result['source'] == 'directory':
            click.echo(f"Directory: {result['directory_path']}")
            click.echo(f"File count: {result['file_count']}")
            click.echo(f"Processing strategy: {result['processing_strategy']}")
            
            if result['processing_strategy'] == 'concatenate':
                click.echo(f"Content length: {len(result['text'])} characters")
            else:
                for i, file_info in enumerate(result['files'][:3], 1):
                    click.echo(f"\nFile {i}: {file_info['file_path']}")
                    content_preview = file_info['content'][:100]
                    click.echo(f"Content preview: {content_preview}..." if len(file_info['content']) > 100 else f"Content: {file_info['content']}")
                
                if len(result['files']) > 3:
                    click.echo(f"\n... and {len(result['files']) - 3} more files")
        else:
            click.echo(f"Content: {result['text'][:100]}..." if len(result['text']) > 100 else f"Content: {result['text']}")

if __name__ == "__main__":
    # Run the CLI if this file is executed directly
    cli() 