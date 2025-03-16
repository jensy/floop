"""
Test script for output formatter.

This script tests the output formatter by formatting a sample response.
"""

from src.output_formatter import clean_text, format_output, format_for_display

def main():
    """Main function to test the output formatter."""
    print("Testing output formatter...")
    
    # Test clean_text
    print("\nTesting clean_text():")
    text = "  This is a   sample text with   excessive whitespace.    "
    cleaned = clean_text(text)
    print(f"Original: '{text}'")
    print(f"Cleaned: '{cleaned}'")
    
    # Test format_output
    print("\nTesting format_output():")
    response = {
        "result": "  This is a   sample result with   excessive whitespace.    ",
        "model": "test-model",
        "input_source": "text",
        "metadata": {
            "model_info": "test-model-v1",
            "usage": {"tokens": 100}
        }
    }
    formatted = format_output(response)
    print(f"Original result: '{response['result']}'")
    print(f"Formatted result: '{formatted['result']}'")
    
    # Test format_for_display
    print("\nTesting format_for_display():")
    text_format = format_for_display(formatted, "text")
    markdown_format = format_for_display(formatted, "markdown")
    print(f"Text format: '{text_format}'")
    print(f"Markdown format:\n{markdown_format}")

if __name__ == "__main__":
    main() 