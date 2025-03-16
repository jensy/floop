"""
Test script for workflow orchestrator.

This script tests the workflow orchestrator by running a simple workflow with Claude.
"""

from src.workflow import run_workflow

def main():
    """Main function to test the workflow orchestrator."""
    print("Testing workflow orchestrator...")
    
    # Test with direct text input and Claude model
    input_text = "Summarize this: The AI workflow MVP is a system that orchestrates multiple AI model interactions in a modular workflow. It allows users to leverage multiple LLMs in a coordinated pipeline for complex tasks on their local environment, ensuring control, flexibility, and privacy."
    print(f"Running workflow with input: '{input_text[:50]}...'")
    
    result = run_workflow(input_text=input_text, model="claude")
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        print("\n✅ Workflow completed successfully!")
        print(f"\nModel: {result['model']}")
        print(f"Input source: {result['input_source']}")
        print(f"\nResult: {result['result']}")
        print(f"\nMetadata: {result['metadata']}")

if __name__ == "__main__":
    main() 