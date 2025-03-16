"""
Configurable Workflow Module

This module extends the workflow orchestrator to support configurable workflows
loaded from JSON configuration files.
"""

import os
import json
import logging
import re
from typing import Dict, Any, Optional, List, Union
import click
from dotenv import load_dotenv

# Import from src package
from src.input_handler import process_input
from src.chatgpt_client import call_chatgpt
from src.claude_client import call_claude
from src.output_formatter import format_output, format_for_display
from src.workflow import run_workflow as run_legacy_workflow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def load_config(config_path: str) -> Optional[Dict[str, Any]]:
    """
    Load a workflow configuration from a JSON file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        The parsed configuration as a dictionary, or None if an error occurred
    """
    try:
        if not os.path.exists(config_path):
            logger.error(f"Configuration file not found: {config_path}")
            return None
            
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        logger.info(f"Successfully loaded configuration from: {config_path}")
        return config
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in configuration file: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        return None

def get_input_from_config(config: Dict[str, Any], cli_input: Optional[str] = None, 
                         cli_input_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Get input from configuration or CLI arguments.
    
    Args:
        config: The workflow configuration
        cli_input: Direct text input from CLI (overrides config)
        cli_input_file: Path to input file from CLI (overrides config)
        
    Returns:
        Dictionary containing the processed input and metadata
    """
    # CLI arguments take precedence over configuration
    if cli_input is not None or cli_input_file is not None:
        logger.info("Using input from CLI arguments (overriding configuration)")
        return process_input(cli_input, cli_input_file)
    
    # Get input from configuration
    input_config = config.get('input', {})
    input_type = input_config.get('type')
    
    if input_type == 'text':
        input_value = input_config.get('value', '')
        logger.info("Using text input from configuration")
        return process_input(input_value, None)
    elif input_type == 'file':
        input_path = input_config.get('path', '')
        logger.info(f"Using file input from configuration: {input_path}")
        return process_input(None, input_path)
    else:
        logger.error(f"Invalid input type in configuration: {input_type}")
        return {"error": f"Invalid input type: {input_type}", "text": None}

def process_template(template: str, context: Dict[str, Any]) -> str:
    """
    Process a prompt template by replacing placeholders with values from context.
    
    Args:
        template: The prompt template with placeholders like {input} or {step_name.output}
        context: Dictionary containing values to replace placeholders
        
    Returns:
        The processed template with placeholders replaced by actual values
    """
    # Find all placeholders in the template
    placeholders = re.findall(r'\{([^}]+)\}', template)
    
    result = template
    for placeholder in placeholders:
        if placeholder == 'input':
            if 'input' in context:
                result = result.replace(f"{{{placeholder}}}", context['input'])
        elif '.' in placeholder:
            # Handle step.output placeholders
            step_name, attribute = placeholder.split('.')
            if step_name in context and attribute in context[step_name]:
                result = result.replace(f"{{{placeholder}}}", context[step_name][attribute])
    
    return result

def execute_step(step_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a single workflow step.
    
    Args:
        step_config: Configuration for the step
        context: Context containing input and outputs from previous steps
        
    Returns:
        Dictionary containing the step result and metadata
    """
    step_name = step_config.get('name', 'unnamed_step')
    model = step_config.get('model')
    model_params = step_config.get('model_params', {})
    prompt_template = step_config.get('prompt_template', '{input}')
    
    # Process the prompt template
    prompt = process_template(prompt_template, context)
    
    logger.info(f"Executing step: {step_name} with model: {model}")
    
    # Execute the step based on the model
    if model == 'chatgpt':
        response = call_chatgpt(
            prompt=prompt,
            model=model_params.get('model', 'gpt-3.5-turbo'),
            max_tokens=model_params.get('max_tokens', 1000),
            temperature=model_params.get('temperature', 0.7)
        )
    elif model == 'claude':
        response = call_claude(
            prompt=prompt,
            model=model_params.get('model', 'claude-3-sonnet-20240229'),
            max_tokens=model_params.get('max_tokens', 1000),
            temperature=model_params.get('temperature', 0.7)
        )
    else:
        logger.error(f"Invalid model: {model}")
        return {"error": f"Invalid model: {model}", "output": None}
    
    # Check for errors
    if "error" in response:
        logger.error(f"Error in step {step_name}: {response['error']}")
        return {"error": response["error"], "output": None}
    
    # Return the result
    return {
        "output": response["text"],
        "model": model,
        "model_info": response.get("model", "unknown"),
        "usage": response.get("usage", {})
    }

def handle_output(result: Dict[str, Any], config: Dict[str, Any], 
                 cli_output_file: Optional[str] = None, 
                 cli_format_type: str = "text") -> Dict[str, Any]:
    """
    Handle the output based on configuration and CLI arguments.
    
    Args:
        result: The workflow result
        config: The workflow configuration
        cli_output_file: Output file path from CLI (overrides config)
        cli_format_type: Output format from CLI (overrides config)
        
    Returns:
        Dictionary containing the output information
    """
    # Get output configuration
    output_config = config.get('output', {})
    output_type = output_config.get('type', 'console')
    
    # CLI arguments take precedence over configuration
    output_path = cli_output_file or output_config.get('path')
    format_type = cli_format_type or output_config.get('format', 'text')
    
    # Format the output
    formatted_result = format_output(result)
    display_output = format_for_display(formatted_result, format_type)
    
    # Handle output based on type
    if output_type == 'file' and output_path:
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Write output to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(display_output)
            logger.info(f"Output saved to file: {output_path}")
            
            return {
                "output_type": "file",
                "output_path": output_path,
                "format": format_type
            }
        except Exception as e:
            logger.error(f"Error saving output to file: {str(e)}")
            return {"error": f"Error saving output to file: {str(e)}"}
    else:
        # Default to console output
        return {
            "output_type": "console",
            "output": display_output,
            "format": format_type
        }

def run_configurable_workflow(
    config: Dict[str, Any],
    input_text: Optional[str] = None,
    input_file: Optional[str] = None,
    output_file: Optional[str] = None,
    format_type: str = "text"
) -> Dict[str, Any]:
    """
    Run a workflow based on a configuration.
    
    Args:
        config: The workflow configuration
        input_text: Direct text input (overrides config)
        input_file: Path to input file (overrides config)
        output_file: Path to output file (overrides config)
        format_type: Output format (overrides config)
        
    Returns:
        Dictionary containing the workflow result and metadata
    """
    # Get input
    input_result = get_input_from_config(config, input_text, input_file)
    
    if "error" in input_result:
        logger.error(f"Input error: {input_result['error']}")
        return {"error": input_result["error"], "result": None}
    
    # Initialize context with input
    context = {
        "input": input_result["text"]
    }
    
    # Execute each step in the workflow
    steps = config.get('steps', [])
    final_step_result = None
    
    for step_config in steps:
        step_name = step_config.get('name', 'unnamed_step')
        step_result = execute_step(step_config, context)
        
        if "error" in step_result:
            logger.error(f"Step error: {step_result['error']}")
            return {"error": step_result["error"], "result": None}
        
        # Add step result to context for use in subsequent steps
        context[step_name] = step_result
        final_step_result = step_result
    
    if not final_step_result:
        logger.error("No steps were executed in the workflow")
        return {"error": "No steps were executed", "result": None}
    
    # Prepare the result
    result = {
        "result": final_step_result["output"],
        "model": final_step_result.get("model", "unknown"),
        "input_source": input_result["source"],
        "metadata": {
            "model_info": final_step_result.get("model_info", "unknown"),
            "usage": final_step_result.get("usage", {})
        },
        "steps": [step.get('name') for step in steps]
    }
    
    # Handle output
    output_result = handle_output(result, config, output_file, format_type)
    
    if "error" in output_result:
        logger.error(f"Output error: {output_result['error']}")
        return {"error": output_result["error"], "result": result}
    
    # Add output information to result
    result["output"] = output_result
    
    logger.info("Workflow completed successfully")
    return result

def run_workflow(
    input_text: Optional[str] = None,
    input_file: Optional[str] = None,
    model: Optional[str] = None,
    max_tokens: int = 1000,
    temperature: float = 0.7,
    format_type: str = "text",
    config_path: Optional[str] = None,
    legacy_mode: bool = False,
    output_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run a workflow based on configuration or legacy mode.
    
    Args:
        input_text: Direct text input
        input_file: Path to input file
        model: The AI model to use (for legacy mode)
        max_tokens: Maximum tokens in response (for legacy mode)
        temperature: Controls randomness (for legacy mode)
        format_type: Output format
        config_path: Path to workflow configuration file
        legacy_mode: Whether to run in legacy mode
        output_file: Path to output file
        
    Returns:
        Dictionary containing the workflow result and metadata
    """
    # If legacy mode is explicitly requested or no config is provided, use legacy workflow
    if legacy_mode or not config_path:
        if not legacy_mode and not config_path:
            logger.info("No configuration provided, falling back to legacy workflow")
        else:
            logger.info("Running in legacy mode")
            
        return run_legacy_workflow(
            input_text=input_text,
            input_file=input_file,
            model=model or "chatgpt",
            max_tokens=max_tokens,
            temperature=temperature,
            format_type=format_type
        )
    
    # Load configuration
    config = load_config(config_path)
    
    if not config:
        logger.error(f"Failed to load configuration from: {config_path}")
        return {"error": f"Failed to load configuration from: {config_path}", "result": None}
    
    # Run configurable workflow
    return run_configurable_workflow(
        config=config,
        input_text=input_text,
        input_file=input_file,
        output_file=output_file,
        format_type=format_type
    )

# CLI interface using Click
@click.command()
@click.option('--input', '-i', help='Direct text input')
@click.option('--input_file', '-f', help='Path to input file')
@click.option('--model', '-m', type=click.Choice(['chatgpt', 'claude', 'claude-first']), 
              default='chatgpt', help='AI model to use (for legacy mode)')
@click.option('--max_tokens', type=int, default=1000, help='Maximum tokens in response (for legacy mode)')
@click.option('--temperature', type=float, default=0.7, help='Temperature (for legacy mode)')
@click.option('--output_file', '-o', help='Path to output file')
@click.option('--format', '-f', 'format_type', type=click.Choice(['text', 'markdown']), 
              default='text', help='Output format')
@click.option('--config', '-c', 'config_path', help='Path to workflow configuration file')
@click.option('--legacy-mode', is_flag=True, help='Run in legacy mode (ignore configuration)')
def cli(input: Optional[str] = None, input_file: Optional[str] = None, 
        model: str = "chatgpt", max_tokens: int = 1000, temperature: float = 0.7,
        output_file: Optional[str] = None, format_type: str = "text",
        config_path: Optional[str] = None, legacy_mode: bool = False):
    """Run the AI workflow with the given input and model."""
    # If no input is provided, prompt the user
    if input is None and input_file is None and not config_path:
        input = click.prompt("Enter your prompt")
    
    result = run_workflow(
        input_text=input,
        input_file=input_file,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        format_type=format_type,
        config_path=config_path,
        legacy_mode=legacy_mode,
        output_file=output_file
    )
    
    if "error" in result:
        click.echo(f"Error: {result['error']}")
        return
    
    # If output is to console, print it
    if not output_file and result.get("output", {}).get("output_type") != "file":
        display_output = result.get("output", {}).get("output", result.get("result", ""))
        
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
        
        # Print steps if available
        if "steps" in result:
            click.echo(f"- Steps: {', '.join(result['steps'])}")

if __name__ == "__main__":
    # Run the CLI if this file is executed directly
    cli() 