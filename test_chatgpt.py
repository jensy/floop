"""
Test script for ChatGPT client.

This script tests the ChatGPT client by sending a simple prompt and printing the response.
"""

from src.chatgpt_client import call_chatgpt

def main():
    """Main function to test the ChatGPT client."""
    print("Testing ChatGPT API...")
    prompt = "Hello, how are you?"
    print(f"Sending prompt: '{prompt}'")
    
    response = call_chatgpt(prompt)
    
    if "error" in response:
        print(f"❌ Error: {response['error']}")
    else:
        print("\n✅ Successfully received response from ChatGPT!")
        print(f"\nChatGPT says: {response['text']}")
        print(f"\nModel used: {response['model']}")
        print(f"Token usage: {response['usage']}")

if __name__ == "__main__":
    main() 