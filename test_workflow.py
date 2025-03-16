"""
Test script for workflow orchestrator.

This script tests the workflow orchestrator by running a simple workflow with Claude.
"""

from src.workflow import run_workflow

def main():
    """Main function to test the workflow orchestrator."""
    print("Testing workflow orchestrator...")
    
    # Test input
    input_text = "Summarize this: Floop is a system that orchestrates multiple AI model interactions in a modular workflow. It allows users to leverage multiple LLMs in a coordinated pipeline for complex tasks on their local environment, ensuring control, flexibility, and privacy."
    print(f"Running workflow with input: '{input_text[:50]}...'")
    
    result = run_workflow(input_text=input_text, model="claude")
    
    # Print the result
    print("\nResult:")
    print(result.get("text", "No result"))
    
    print("\n✅ Workflow completed successfully!")

if __name__ == "__main__":
    main() 