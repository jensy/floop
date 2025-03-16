"""
Configurable Workflow Module

This module extends the workflow orchestrator to support configurable workflows
loaded from JSON configuration files.
"""

import os
import sys
import json
import logging
import re
from typing import Dict, Any, Optional, List, Union
import click
from dotenv import load_dotenv

# Add the parent directory to sys.path to allow imports when run directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import from src package
try:
    # Try importing as a module first
    from src.input_handler import process_input
    from src.chatgpt_client import call_chatgpt
    from src.claude_client import call_claude
    from src.web_search_client import call_web_search
    from src.output_formatter import format_output, format_for_display, save_results_to_file
except ModuleNotFoundError:
    # If that fails, import directly
    from input_handler import process_input
    from chatgpt_client import call_chatgpt
    from claude_client import call_claude
    from web_search_client import call_web_search
    from output_formatter import format_output, format_for_display, save_results_to_file

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
                         cli_input_file: Optional[str] = None,
                         cli_input_directory: Optional[str] = None,
                         cli_file_pattern: str = "*.txt",
                         cli_recursive: bool = False,
                         cli_processing_strategy: str = "individual",
                         cli_web_search: Optional[str] = None) -> Dict[str, Any]:
    """
    Get input from configuration or CLI arguments.
    
    Args:
        config: The workflow configuration
        cli_input: Direct text input from CLI (overrides config)
        cli_input_file: Path to input file from CLI (overrides config)
        cli_input_directory: Path to input directory from CLI (overrides config)
        cli_file_pattern: File pattern for directory input from CLI
        cli_recursive: Whether to search recursively in subdirectories from CLI
        cli_processing_strategy: How to process directory files from CLI
        cli_web_search: Web search query from CLI (overrides config)
        
    Returns:
        Dictionary containing the processed input and metadata
    """
    # CLI arguments take precedence over configuration
    if cli_web_search is not None:
        logger.info("Using web search query from CLI arguments (overriding configuration)")
        return {"text": cli_web_search, "source": "web_search_query"}
    elif cli_input is not None or cli_input_file is not None or cli_input_directory is not None:
        logger.info("Using input from CLI arguments (overriding configuration)")
        return process_input(cli_input, cli_input_file, cli_input_directory, 
                           cli_file_pattern, cli_recursive, cli_processing_strategy)
    
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
    elif input_type == 'directory':
        input_path = input_config.get('path', '')
        file_pattern = input_config.get('file_pattern', '*.txt')
        recursive = input_config.get('recursive', False)
        processing_strategy = input_config.get('processing_strategy', 'individual')
        logger.info(f"Using directory input from configuration: {input_path}")
        return process_input(None, None, input_path, file_pattern, recursive, processing_strategy)
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
    Execute a single workflow step based on the provided configuration and context.
    
    Args:
        step_config: The step configuration
        context: The current context containing previous step results
        
    Returns:
        Dictionary containing the step result and metadata
    """
    step_name = step_config.get('name', 'unnamed_step')
    model = step_config.get('model', 'chatgpt')
    prompt_template = step_config.get('prompt_template', '{input}')
    model_params = step_config.get('model_params', {})
    
    # Process the prompt template with the current context
    try:
        input_data = prompt_template.format(**context)
    except KeyError as e:
        logger.error(f"Error formatting prompt template: {str(e)}")
        return {"error": f"Missing context variable: {str(e)}", "output": None}
    
    logger.info(f"Executing step {step_name} with model {model}")
    
    # Execute the step based on the model
    if model == 'chatgpt':
        max_tokens = model_params.get('max_tokens', 1000)
        temperature = model_params.get('temperature', 0.7)
        response = call_chatgpt(input_data, max_tokens=max_tokens, temperature=temperature)
    elif model == 'claude':
        max_tokens = model_params.get('max_tokens', 1000)
        temperature = model_params.get('temperature', 0.7)
        response = call_claude(input_data, max_tokens=max_tokens, temperature=temperature)
    elif model == 'web_search':
        response = call_web_search(input_data)
    else:
        logger.error(f"Invalid model: {model}")
        return {"error": f"Invalid model: {model}", "output": None}
    
    # Check for errors
    if "error" in response:
        logger.error(f"Error in step {step_name}: {response['error']}")
        return {"error": response["error"], "output": None}
    
    # Extract the output text from the response
    output_text = response.get("text", "")
    
    # Return the result with all necessary fields for formatting
    return {
        "output": output_text,
        "text": output_text,
        "model": model,
        "model_info": response.get("model", model),
        "usage": response.get("usage", {}),
        "step_name": step_name,
        "task": step_config.get('task', f'Step {step_name}')
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
    
    logger.info(f"Using output format: {format_type}")
    
    # Format the output
    formatted_result = format_output(result)
    
    # Handle output based on type
    if output_type == 'file' or output_path:
        try:
            # Format the output for display based on the format type
            display_output = format_for_display(formatted_result, format_type)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Save results to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(display_output)
            
            logger.info(f"Output saved to file: {output_path}")
            return {
                "output_type": "file",
                "output_path": output_path,
                "format": format_type,
                "result": formatted_result,
                "output": display_output
            }
        except Exception as e:
            logger.error(f"Error saving output to file: {str(e)}")
            return {"error": f"Error saving output to file: {str(e)}"}
    else:
        # Default to console output
        display_output = format_for_display(formatted_result, format_type)
        return {
            "output_type": "console",
            "output": display_output,
            "format": format_type,
            "result": formatted_result
        }

def run_configurable_workflow(
    config: Dict[str, Any],
    input_text: Optional[str] = None,
    input_file: Optional[str] = None,
    input_directory: Optional[str] = None,
    file_pattern: str = "*.txt",
    recursive: bool = False,
    processing_strategy: str = "individual",
    output_file: Optional[str] = None,
    format_type: str = "text",
    web_search: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run a workflow based on a configuration.
    
    Args:
        config: The workflow configuration
        input_text: Direct text input (overrides config)
        input_file: Path to input file (overrides config)
        input_directory: Path to input directory (overrides config)
        file_pattern: File pattern for directory input
        recursive: Whether to search recursively in subdirectories
        processing_strategy: How to process directory files
        output_file: Path to output file (overrides config)
        format_type: Output format (overrides config)
        web_search: Web search query (overrides config)
        
    Returns:
        Dictionary containing the workflow result and metadata
    """
    # Get input
    input_result = get_input_from_config(
        config, input_text, input_file, input_directory, 
        file_pattern, recursive, processing_strategy, web_search
    )
    
    if "error" in input_result:
        return input_result
    
    # Get output configuration
    output_config = config.get('output', {})
    config_format_type = output_config.get('format', 'text')
    
    # CLI format type takes precedence over configuration
    if not format_type or format_type == "text":
        format_type = config_format_type
    
    logger.info(f"Using format type: {format_type}")
    
    # Check if we have AI models defined in the configuration
    if 'ai_models' in config:
        # Process AI models in sequence
        context = {'input': input_result.get('text', '')}
        steps = []
        
        for i, model_config in enumerate(config['ai_models']):
            model_name = model_config.get('name')
            task = model_config.get('task', f'Step {i+1}')
            
            logger.info(f"Processing AI model: {model_name} - {task}")
            
            # Create step configuration
            step_config = {
                'name': f'step_{i+1}',
                'model': model_name,
                'prompt_template': '{input}',
                'model_params': model_config.get('parameters', {}),
                'task': task
            }
            
            # Execute the step
            step_result = execute_step(step_config, context)
            
            if "error" in step_result:
                return step_result
            
            # Add step result to context for next step
            context[f'step_{i+1}'] = step_result
            context['input'] = step_result.get('output', '')
            
            # Add step to steps list
            steps.append(f'step_{i+1}')
        
        # Use the last step's result as the final result
        final_step = f'step_{len(config["ai_models"])}'
        final_result = context.get(final_step, {})
        
        # Add steps to the final result
        final_result['steps'] = steps
        
        # Add all step results to the final result
        for step in steps:
            final_result[step] = context.get(step, {})
        
        # Handle output
        output_result = handle_output(final_result, config, output_file, format_type)
        
        return output_result
    else:
        # Get model configuration
        model_config = config.get('model', {})
        model_type = model_config.get('type', 'chatgpt')
        
        # Check if web search is requested
        if web_search is not None:
            model_type = "web_search"
        
        # Call AI model
        if model_type == "chatgpt":
            model_result = call_chatgpt(input_result)
        elif model_type == "claude":
            model_result = call_claude(input_result)
        elif model_type == "web_search":
            model_result = call_web_search(input_result)
        else:
            return {"error": f"Invalid model type: {model_type}"}
        
        if "error" in model_result:
            return model_result
        
        # Handle output
        output_result = handle_output(model_result, config, output_file, format_type)
        
        return output_result

def run_workflow(
    input_text: Optional[str] = None,
    input_file: Optional[str] = None,
    input_directory: Optional[str] = None,
    file_pattern: str = "*.txt",
    recursive: bool = False,
    processing_strategy: str = "individual",
    model: Optional[str] = None,
    max_tokens: int = 1000,
    temperature: float = 0.7,
    format_type: str = "text",
    config_path: Optional[str] = None,
    legacy_mode: bool = False,
    output_file: Optional[str] = None,
    web_search: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run a workflow based on configuration or legacy mode.
    
    Args:
        input_text: Direct text input
        input_file: Path to input file
        input_directory: Path to input directory
        file_pattern: File pattern for directory input
        recursive: Whether to search recursively in subdirectories
        processing_strategy: How to process directory files
        model: The AI model to use (for legacy mode)
        max_tokens: Maximum tokens in response (for legacy mode)
        temperature: Controls randomness (for legacy mode)
        format_type: Output format
        config_path: Path to workflow configuration file
        legacy_mode: Whether to run in legacy mode
        output_file: Path to output file
        web_search: Web search query (overrides other input methods)
        
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
            input_directory=input_directory,
            file_pattern=file_pattern,
            recursive=recursive,
            processing_strategy=processing_strategy,
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
        input_directory=input_directory,
        file_pattern=file_pattern,
        recursive=recursive,
        processing_strategy=processing_strategy,
        output_file=output_file,
        format_type=format_type,
        web_search=web_search
    )

# CLI interface using Click
@click.command()
@click.option('--input', '-i', help='Direct text input')
@click.option('--input_file', '-f', help='Path to input file')
@click.option('--input_directory', '-d', help='Path to input directory')
@click.option('--file_pattern', default='*.txt', help='File pattern for directory input (default: *.txt)')
@click.option('--recursive', is_flag=True, help='Search recursively in subdirectories')
@click.option('--processing_strategy', type=click.Choice(['individual', 'concatenate']), 
              default='individual', help='How to process directory files')
@click.option('--model', '-m', type=click.Choice(['chatgpt', 'claude', 'claude-first', 'web_search']), 
              default='chatgpt', help='AI model to use (for legacy mode)')
@click.option('--max_tokens', type=int, default=1000, help='Maximum tokens in response (for legacy mode)')
@click.option('--temperature', type=float, default=0.7, help='Temperature (for legacy mode)')
@click.option('--output_file', '-o', help='Path to output file')
@click.option('--format', 'format_type', type=click.Choice(['text', 'markdown', 'json', 'html']), 
              default='text', help='Output format')
@click.option('--config', '-c', 'config_path', help='Path to workflow configuration file')
@click.option('--legacy-mode', is_flag=True, help='Run in legacy mode (ignore configuration)')
@click.option('--web_search', '-ws', help='Web search query (overrides other input methods)')
def cli(input: Optional[str] = None, input_file: Optional[str] = None, 
        input_directory: Optional[str] = None, file_pattern: str = '*.txt',
        recursive: bool = False, processing_strategy: str = 'individual',
        model: str = "chatgpt", max_tokens: int = 1000, temperature: float = 0.7,
        output_file: Optional[str] = None, format_type: str = "text",
        config_path: Optional[str] = None, legacy_mode: bool = False,
        web_search: Optional[str] = None):
    """Run the AI workflow with the given input and model."""
    # If no input is provided, prompt the user
    if input is None and input_file is None and input_directory is None and not config_path:
        input = click.prompt("Enter your prompt")
    
    result = run_workflow(
        input_text=input,
        input_file=input_file,
        input_directory=input_directory,
        file_pattern=file_pattern,
        recursive=recursive,
        processing_strategy=processing_strategy,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        format_type=format_type,
        config_path=config_path,
        legacy_mode=legacy_mode,
        output_file=output_file,
        web_search=web_search
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