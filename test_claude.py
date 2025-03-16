"""
Test script for Claude client.

This script tests the Claude client by sending a simple prompt and printing the response.
"""

from src.claude_client import call_claude

def main():
    """Main function to test the Claude client."""
    print("Testing Claude API...")
    prompt = "Explain quantum physics in simple terms"
    print(f"Sending prompt: '{prompt}'")
    
    response = call_claude(prompt)
    
    if "error" in response:
        print(f"❌ Error: {response['error']}")
    else:
        print("\n✅ Successfully received response from Claude!")
        print(f"\nClaude says: {response['text']}")
        print(f"\nModel used: {response['model']}")
        print(f"Token usage: {response['usage']}")

if __name__ == "__main__":
    main() 