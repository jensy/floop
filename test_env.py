import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API keys
openai_api_key = os.getenv("OPENAI_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

# Print API keys (in a real application, you would never print API keys)
print(f"OpenAI API Key: {openai_api_key}")
print(f"Anthropic API Key: {anthropic_api_key}")

# Check if API keys are loaded
if openai_api_key and anthropic_api_key:
    print("✅ API keys loaded successfully!")
else:
    print("❌ Failed to load API keys. Please check your .env file.") 