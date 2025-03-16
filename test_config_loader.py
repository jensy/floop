"""
Test script for loading workflow configuration.

This script tests loading and parsing a workflow configuration file.
"""

import json
import os
import sys

def load_config(config_path):
    """
    Load a workflow configuration from a JSON file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        The parsed configuration as a dictionary
    """
    try:
        if not os.path.exists(config_path):
            print(f"Error: Configuration file not found: {config_path}")
            return None
            
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        print(f"Successfully loaded configuration from: {config_path}")
        return config
        
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in configuration file: {str(e)}")
        return None
    except Exception as e:
        print(f"Error loading configuration: {str(e)}")
        return None

def main():
    """Main function to test loading a workflow configuration."""
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = "configs/workflow_config.json"
    
    print(f"Loading configuration from: {config_path}")
    config = load_config(config_path)
    
    if config:
        print("\nConfiguration details:")
        print(f"Name: {config.get('name')}")
        print(f"Description: {config.get('description')}")
        
        print("\nInput:")
        input_config = config.get('input', {})
        print(f"Type: {input_config.get('type')}")
        if input_config.get('type') == 'text':
            print(f"Value: {input_config.get('value')}")
        elif input_config.get('type') == 'file':
            print(f"Path: {input_config.get('path')}")
        
        print("\nSteps:")
        for i, step in enumerate(config.get('steps', [])):
            print(f"Step {i+1}: {step.get('name')}")
            print(f"  Model: {step.get('model')}")
            print(f"  Prompt template: {step.get('prompt_template')}")
        
        print("\nOutput:")
        output_config = config.get('output', {})
        print(f"Type: {output_config.get('type')}")
        print(f"Format: {output_config.get('format')}")
        if output_config.get('type') == 'file':
            print(f"Path: {output_config.get('path')}")

if __name__ == "__main__":
    main() 