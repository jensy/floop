"""
Test script for directory input functionality.

This script tests the directory input functionality by processing files in the sample_data directory.
"""

import os
import sys
from src.input_handler import process_input
from src.workflow import run_workflow

def test_directory_input():
    """Test the directory input functionality."""
    print("Testing directory input functionality...")
    
    # Test with individual processing
    print("\n1. Testing directory input with individual processing:")
    result = process_input(
        input_directory="sample_data",
        file_pattern="*.txt",
        recursive=True,
        processing_strategy="individual"
    )
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    print(f"Source: {result['source']}")
    print(f"Directory: {result['directory_path']}")
    print(f"File count: {result['file_count']}")
    print(f"Processing strategy: {result['processing_strategy']}")
    
    print("\nFiles found:")
    for i, file_info in enumerate(result['files'], 1):
        print(f"{i}. {file_info['file_path']} ({len(file_info['content'])} characters)")
    
    # Test with concatenated processing
    print("\n2. Testing directory input with concatenated processing:")
    result = process_input(
        input_directory="sample_data",
        file_pattern="*.txt",
        recursive=True,
        processing_strategy="concatenate"
    )
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    print(f"Source: {result['source']}")
    print(f"Directory: {result['directory_path']}")
    print(f"File count: {result['file_count']}")
    print(f"Processing strategy: {result['processing_strategy']}")
    print(f"Combined content length: {len(result['text'])} characters")
    print(f"Content preview: {result['text'][:100]}...")

def test_workflow_with_directory():
    """Test the workflow with directory input."""
    print("\n3. Testing workflow with directory input (individual processing):")
    
    # Skip actual API calls if no API keys are set
    if not os.environ.get("OPENAI_API_KEY") and not os.environ.get("ANTHROPIC_API_KEY"):
        print("Skipping workflow test as no API keys are set.")
        return
    
    result = run_workflow(
        input_directory="sample_data",
        file_pattern="*.txt",
        recursive=True,
        processing_strategy="individual",
        model="claude",
        max_tokens=100,
        temperature=0.7,
        format_type="markdown"
    )
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    print(f"Model: {result['model']}")
    print(f"Input source: {result['input_source']}")
    print(f"Directory: {result['directory_path']}")
    print(f"File count: {result['file_count']}")
    print(f"Successful files: {result['metadata']['successful_files']}")
    print(f"Failed files: {result['metadata']['failed_files']}")
    
    print("\nFirst 2 results:")
    for i, file_result in enumerate(result['results'][:2], 1):
        print(f"\nResult {i}:")
        print(f"File: {file_result.get('file_path', 'unknown')}")
        
        if "error" in file_result:
            print(f"Error: {file_result['error']}")
        else:
            print(f"Result preview: {file_result.get('result', '')[:100]}...")

def main():
    """Main function to run the tests."""
    print("=== Directory Input Tests ===")
    
    # Test directory input functionality
    test_directory_input()
    
    # Test workflow with directory input
    test_workflow_with_directory()
    
    print("\nTests completed.")

if __name__ == "__main__":
    main() 