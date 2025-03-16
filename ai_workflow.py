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
from src.workflow import run_workflow
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
def cli(input: Optional[str] = None, input_file: Optional[str] = None, 
        use_chatgpt: bool = False, use_claude: bool = False,
        model: Optional[str] = None, max_tokens: int = 1000, 
        temperature: float = 0.7, output_file: Optional[str] = None,
        format_type: str = "text"):
    """
    Run the AI workflow with the given input and model.
    
    This tool orchestrates interactions between multiple AI models (ChatGPT and Claude)
    to process text input and generate responses.
    """
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
    
    logger.info(f"Running workflow with model: {model}")
    result = run_workflow(input, input_file, model, max_tokens, temperature, format_type)
    
    if "error" in result:
        click.echo(f"Error: {result['error']}")
        return
    
    # Format the output for display
    display_output = format_for_display(result, format_type)
    
    # Output to file if specified
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(display_output)
            click.echo(f"Output saved to {output_file}")
        except Exception as e:
            click.echo(f"Error saving output to file: {str(e)}")
    else:
        # Print to console
        click.echo("\n" + "="*50)
        click.echo(f"Workflow Result (model: {result['model']})")
        click.echo("="*50)
        click.echo(display_output)
        click.echo("="*50)
        
        # Print metadata
        click.echo(f"\nMetadata:")
        click.echo(f"- Model: {result['metadata']['model_info']}")
        click.echo(f"- Input source: {result['input_source']}")
        click.echo(f"- Token usage: {result['metadata']['usage']}")
        
        # Print Claude's response if available
        if "claude_response" in result:
            click.echo("\n" + "="*50)
            click.echo("Claude's Initial Response:")
            click.echo("="*50)
            click.echo(result["claude_response"])
            click.echo("="*50)

if __name__ == "__main__":
    cli() 