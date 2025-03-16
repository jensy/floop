"""
Test script for configurable workflow.

This script tests the configurable workflow module by running a workflow with a configuration file.
"""

import sys
import click
from src.config_workflow import run_workflow

def main():
    """Main function to test the configurable workflow."""
    # Get configuration file path from command line arguments
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = "configs/workflow_config.json"
    
    # Get optional CLI arguments
    input_text = None
    input_file = None
    output_file = None
    format_type = "text"
    legacy_mode = False
    
    # Parse additional command line arguments
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--input" or arg == "-i":
            if i + 1 < len(sys.argv):
                input_text = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        elif arg == "--input_file" or arg == "-f":
            if i + 1 < len(sys.argv):
                input_file = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        elif arg == "--output_file" or arg == "-o":
            if i + 1 < len(sys.argv):
                output_file = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        elif arg == "--format":
            if i + 1 < len(sys.argv):
                format_type = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        elif arg == "--legacy-mode":
            legacy_mode = True
            i += 1
        else:
            i += 1
    
    print(f"Testing configurable workflow with configuration: {config_path}")
    if input_text:
        print(f"Input text: {input_text}")
    if input_file:
        print(f"Input file: {input_file}")
    if output_file:
        print(f"Output file: {output_file}")
    print(f"Format: {format_type}")
    if legacy_mode:
        print("Running in legacy mode")
    
    # Run the workflow
    result = run_workflow(
        input_text=input_text,
        input_file=input_file,
        config_path=config_path,
        legacy_mode=legacy_mode,
        output_file=output_file,
        format_type=format_type
    )
    
    # Check the result
    if "error" in result:
        print(f"\n❌ Error: {result['error']}")
    else:
        print("\n✅ Workflow completed successfully!")
        
        # Print workflow information
        print(f"\nWorkflow information:")
        print(f"- Model: {result['model']}")
        print(f"- Input source: {result['input_source']}")
        
        # Print steps if available
        if "steps" in result:
            print(f"- Steps: {', '.join(result['steps'])}")
        
        # Print output information
        output_info = result.get("output", {})
        print(f"\nOutput information:")
        print(f"- Type: {output_info.get('output_type', 'unknown')}")
        print(f"- Format: {output_info.get('format', 'unknown')}")
        if output_info.get("output_type") == "file":
            print(f"- Path: {output_info.get('output_path', 'unknown')}")

if __name__ == "__main__":
    main() 