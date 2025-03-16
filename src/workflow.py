"""
Workflow Orchestrator Module

This module orchestrates the AI workflow by routing input to the selected AI model
and retrieving the response.
"""

import os
import logging
from typing import Dict, Any, Optional, Literal
import click
from dotenv import load_dotenv

# Import from src package
from src.input_handler import process_input
from src.chatgpt_client import call_chatgpt
from src.claude_client import call_claude
from src.output_formatter import format_output, format_for_display

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def run_workflow(
    input_text: Optional[str] = None,
    input_file: Optional[str] = None,
    model: Literal["chatgpt", "claude", "claude-first"] = "chatgpt",
    max_tokens: int = 1000,
    temperature: float = 0.7,
    format_type: str = "text"
) -> Dict[str, Any]:
    """
    Run the AI workflow with the given input and model.
    
    Args:
        input_text: Direct text input
        input_file: Path to input file
        model: The AI model to use (chatgpt, claude, or claude-first for multi-step)
        max_tokens: Maximum number of tokens in the response
        temperature: Controls randomness (0-1)
        format_type: The format to use for display (text, markdown)
        
    Returns:
        Dictionary containing the workflow result and metadata
    """
    # Process input
    logger.info("Processing input...")
    input_result = process_input(input_text, input_file)
    
    if "error" in input_result:
        logger.error(f"Input error: {input_result['error']}")
        return {"error": input_result["error"], "result": None}
    
    prompt = input_result["text"]
    logger.info(f"Input processed successfully (source: {input_result['source']})")
    
    # Run the workflow based on the selected model
    if model == "chatgpt":
        logger.info("Running workflow with ChatGPT...")
        response = call_chatgpt(prompt, max_tokens=max_tokens, temperature=temperature)
    elif model == "claude":
        logger.info("Running workflow with Claude...")
        response = call_claude(prompt, max_tokens=max_tokens, temperature=temperature)
    elif model == "claude-first":
        logger.info("Running multi-step workflow (Claude -> ChatGPT)...")
        
        # First, call Claude
        logger.info("Step 1: Calling Claude...")
        claude_response = call_claude(prompt, max_tokens=max_tokens, temperature=temperature)
        
        if "error" in claude_response:
            logger.error(f"Claude error: {claude_response['error']}")
            return {"error": claude_response["error"], "result": None}
        
        # Then, use Claude's response as input for ChatGPT
        logger.info("Step 2: Calling ChatGPT with Claude's response...")
        chatgpt_prompt = f"Here's an analysis from another AI assistant: {claude_response['text']}\n\nPlease review and refine this analysis."
        response = call_chatgpt(chatgpt_prompt, max_tokens=max_tokens, temperature=temperature)
        
        # Add Claude's response to the result
        if "error" not in response:
            response["claude_response"] = claude_response["text"]
    else:
        logger.error(f"Invalid model: {model}")
        return {"error": f"Invalid model: {model}", "result": None}
    
    # Check for errors
    if "error" in response:
        logger.error(f"Model error: {response['error']}")
        return {"error": response["error"], "result": None}
    
    # Return the result
    logger.info("Workflow completed successfully")
    result = {
        "result": response["text"],
        "model": model,
        "input_source": input_result["source"],
        "metadata": {
            "model_info": response.get("model", "unknown"),
            "usage": response.get("usage", {})
        }
    }
    
    # Format the output
    formatted_result = format_output(result)
    
    return formatted_result

# CLI interface using Click
@click.command()
@click.option('--input', '-i', help='Direct text input')
@click.option('--input_file', '-f', help='Path to input file')
@click.option('--model', '-m', type=click.Choice(['chatgpt', 'claude', 'claude-first']), 
              default='chatgpt', help='AI model to use')
@click.option('--max_tokens', type=int, default=1000, help='Maximum tokens in response')
@click.option('--temperature', type=float, default=0.7, help='Temperature (randomness)')
@click.option('--format', '-f', 'format_type', type=click.Choice(['text', 'markdown']), 
              default='text', help='Output format')
def cli(input: Optional[str] = None, input_file: Optional[str] = None, 
        model: str = "chatgpt", max_tokens: int = 1000, temperature: float = 0.7,
        format_type: str = "text"):
    """Run the AI workflow with the given input and model."""
    # If no input is provided, prompt the user
    if input is None and input_file is None:
        input = input("Enter your prompt: ")
    
    result = run_workflow(input, input_file, model, max_tokens, temperature, format_type)
    
    if "error" in result:
        click.echo(f"Error: {result['error']}")
    else:
        # Format the output for display
        display_output = format_for_display(result, format_type)
        
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
    # Run the CLI if this file is executed directly
    cli() 