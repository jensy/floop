"""
Test script for error handling.

This script tests error handling by intentionally causing errors and checking the response.
"""

import os
from openai import OpenAI
from src.chatgpt_client import call_chatgpt, client as openai_client
from src.claude_client import call_claude

def test_invalid_api_key():
    """Test error handling with an invalid API key."""
    print("Testing error handling with invalid API key...")
    
    # Save the original client
    original_client = openai_client
    
    try:
        # Create a new client with an invalid API key
        invalid_client = OpenAI(api_key="this_is_not_a_valid_api_key_format")
        
        # Replace the client in the module
        import src.chatgpt_client
        src.chatgpt_client.client = invalid_client
        
        # Call ChatGPT with the invalid client
        print("Calling ChatGPT with invalid API key...")
        response = call_chatgpt("Hello, how are you?", max_retries=1, retry_delay=0.1)
        
        # Check if the error was handled properly
        if "error" in response:
            print(f"\n✅ Error handled properly!")
            print(f"Error message: {response['error']}")
        else:
            print(f"\n❌ Error not handled properly!")
            print(f"Response: {response}")
            
    finally:
        # Restore the original client
        src.chatgpt_client.client = original_client

def main():
    """Main function to test error handling."""
    test_invalid_api_key()

if __name__ == "__main__":
    main() 