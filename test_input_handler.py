"""
Test script for input handler.

This script tests the input handler by reading from a file and printing the content.
"""

from src.input_handler import process_input

def main():
    """Main function to test the input handler."""
    print("Testing input handler...")
    
    # Test file input
    input_file = "sample.txt"
    print(f"Reading from file: {input_file}")
    
    result = process_input(input_file=input_file)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        print("\n✅ Successfully processed input!")
        print(f"Source: {result['source']}")
        print(f"File: {result['file_path']}")
        print(f"Content: {result['text']}")

if __name__ == "__main__":
    main() 