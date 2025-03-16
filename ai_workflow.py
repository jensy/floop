#!/usr/bin/env python3
"""
AI Workflow MVP

This script provides a command-line interface to the AI workflow MVP.
It orchestrates interactions between multiple AI models (ChatGPT and Claude)
to process text input and generate responses.
"""

import os
import sys
import logging
from typing import Optional
import click
from dotenv import load_dotenv

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import modules from src
from src.input_handler import process_input
from src.workflow import run_workflow as run_legacy_workflow
from src.config_workflow import run_workflow as run_configurable_workflow
from src.output_formatter import format_for_display

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("workflow.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

@click.command()
@click.option('--input', '-i', help='Direct text input')
@click.option('--input_file', '-f', help='Path to input file')
@click.option('--use_chatgpt', is_flag=True, help='Use ChatGPT model')
@click.option('--use_claude', is_flag=True, help='Use Claude model')
@click.option('--model', '-m', type=click.Choice(['chatgpt', 'claude', 'claude-first']), 
              default=None, help='AI model to use (alternative to --use_* flags)')
@click.option('--max_tokens', type=int, default=1000, help='Maximum tokens in response')
@click.option('--temperature', type=float, default=0.7, help='Temperature (randomness)')
@click.option('--output_file', '-o', help='Path to output file')
@click.option('--format', '-f', 'format_type', type=click.Choice(['text', 'markdown']), 
              default='text', help='Output format')
@click.option('--config', '-c', help='Path to workflow configuration file')
@click.option('--legacy-mode', is_flag=True, help='Run in legacy mode (ignore configuration)')
def cli(input: Optional[str] = None, input_file: Optional[str] = None, 
        use_chatgpt: bool = False, use_claude: bool = False,
        model: Optional[str] = None, max_tokens: int = 1000, 
        temperature: float = 0.7, output_file: Optional[str] = None,
        format_type: str = "text", config: Optional[str] = None,
        legacy_mode: bool = False):
    """
    Run the AI workflow with the given input and model.
    
    This tool orchestrates interactions between multiple AI models (ChatGPT and Claude)
    to process text input and generate responses.
    """
    # If legacy mode is explicitly requested or no config is provided, use legacy workflow
    if legacy_mode or not config:
        # Determine the model to use
        if model is None:
            if use_chatgpt and use_claude:
                model = "claude-first"  # Multi-step workflow
            elif use_chatgpt:
                model = "chatgpt"
            elif use_claude:
                model = "claude"
            else:
                model = "chatgpt"  # Default to ChatGPT
        
        # If no input is provided, prompt the user
        if input is None and input_file is None:
            input = click.prompt("Enter your prompt")
        
        logger.info(f"Running legacy workflow with model: {model}")
        result = run_legacy_workflow(input, input_file, model, max_tokens, temperature, format_type)
    else:
        # Run configurable workflow
        logger.info(f"Running configurable workflow with configuration: {config}")
        result = run_configurable_workflow(
            input_text=input,
            input_file=input_file,
            config_path=config,
            legacy_mode=False,
            output_file=output_file,
            format_type=format_type
        )
    
    if "error" in result:
        click.echo(f"Error: {result['error']}")
        return
    
    # If using legacy workflow or output is to console, print it
    if legacy_mode or not config or (not output_file and result.get("output", {}).get("output_type") != "file"):
        # Format the output for display
        if legacy_mode or not config:
            display_output = format_for_display(result, format_type)
        else:
            display_output = result.get("output", {}).get("output", result.get("result", ""))
        
        # Output to file if specified in legacy mode
        if output_file and (legacy_mode or not config):
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(display_output)
                click.echo(f"Output saved to {output_file}")
            except Exception as e:
                click.echo(f"Error saving output to file: {str(e)}")
        else:
            # Print to console
            click.echo("\n" + "="*50)
            click.echo(f"Workflow Result (model: {result.get('model', 'unknown')})")
            click.echo("="*50)
            click.echo(display_output)
            click.echo("="*50)
            
            # Print metadata
            click.echo(f"\nMetadata:")
            if "metadata" in result:
                click.echo(f"- Model: {result['metadata'].get('model_info', 'unknown')}")
                click.echo(f"- Token usage: {result['metadata'].get('usage', {})}")
            click.echo(f"- Input source: {result.get('input_source', 'unknown')}")
            
            # Print steps if available
            if "steps" in result:
                click.echo(f"- Steps: {', '.join(result['steps'])}")
            
            # Print Claude's response if available in legacy mode
            if "claude_response" in result:
                click.echo("\n" + "="*50)
                click.echo("Claude's Initial Response:")
                click.echo("="*50)
                click.echo(result["claude_response"])
                click.echo("="*50)

if __name__ == "__main__":
    cli() 