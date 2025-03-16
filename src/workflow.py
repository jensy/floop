"""
Workflow Orchestrator Module

This module orchestrates the AI workflow by routing input to the selected AI model
and retrieving the response.
"""

import os
import sys
import logging
import json
from typing import Dict, Any, Optional, Literal, List
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

def process_single_input(
    input_content: str,
    model: Literal["chatgpt", "claude", "claude-first", "web_search"] = "chatgpt",
    max_tokens: int = 1000,
    temperature: float = 0.7,
    source_info: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Process a single input with the selected AI model.
    
    Args:
        input_content: The text content to process
        model: The AI model to use
        max_tokens: Maximum number of tokens in the response
        temperature: Controls randomness (0-1)
        source_info: Information about the source of the input
        
    Returns:
        Dictionary containing the result and metadata
    """
    # Run the workflow based on the selected model
    if model == "chatgpt":
        logger.info("Running workflow with ChatGPT...")
        response = call_chatgpt(input_content, max_tokens=max_tokens, temperature=temperature)
    elif model == "claude":
        logger.info("Running workflow with Claude...")
        response = call_claude(input_content, max_tokens=max_tokens, temperature=temperature)
    elif model == "web_search":
        logger.info("Running workflow with web search...")
        response = call_web_search(input_content)
    elif model == "claude-first":
        logger.info("Running multi-step workflow (Claude -> ChatGPT)...")
        
        # First, call Claude
        logger.info("Step 1: Calling Claude...")
        claude_response = call_claude(input_content, max_tokens=max_tokens, temperature=temperature)
        
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
    result = {
        "result": response["text"],
        "model": model,
        "input_source": source_info.get("source") if source_info else "unknown",
        "metadata": {
            "model_info": response.get("model", "unknown"),
            "usage": response.get("usage", {})
        }
    }
    
    # Add source info if available
    if source_info:
        result.update(source_info)
        
    # Add Claude's response if available
    if "claude_response" in response:
        result["claude_response"] = response["claude_response"]
    
    return result

def run_workflow(
    input_text: Optional[str] = None,
    input_file: Optional[str] = None,
    input_directory: Optional[str] = None,
    file_pattern: str = "*.txt",
    recursive: bool = False,
    processing_strategy: str = "individual",
    model: str = "chatgpt",
    output_file: Optional[str] = None,
    format_type: str = "text",
    web_search: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run the AI workflow.
    
    Args:
        input_text: Direct text input
        input_file: Path to input file
        input_directory: Path to input directory
        file_pattern: File pattern for directory input
        recursive: Whether to search recursively in subdirectories
        processing_strategy: How to process directory files
        model: AI model to use
        output_file: Path to output file
        format_type: Output format
        web_search: Web search query (overrides other input methods)
        
    Returns:
        Dictionary containing the workflow result and metadata
    """
    logger = logging.getLogger(__name__)
    
    # Check if web search is provided
    if web_search:
        logger.info(f"Using web search query: {web_search}")
        input_result = {"text": web_search, "source": "web_search_query"}
        model = "web_search"
    else:
        # Process input
        input_result = process_input(input_text, input_file, input_directory, 
                                   file_pattern, recursive, processing_strategy)
    
    if "error" in input_result:
        return input_result
    
    # Call AI model
    if model == "chatgpt":
        model_result = call_chatgpt(input_result)
    elif model == "claude":
        model_result = call_claude(input_result)
    elif model == "web_search":
        model_result = call_web_search(input_result)
    else:
        return {"error": f"Invalid model: {model}"}
    
    if "error" in model_result:
        return model_result
    
    # Format output
    formatted_result = format_output(model_result)
    
    # Handle output
    if output_file:
        try:
            # Save results to file
            success = save_results_to_file(formatted_result, output_file, format_type)
            
            if success:
                logger.info(f"Output saved to file: {output_file}")
                # Return the formatted result directly
                return formatted_result
            else:
                logger.error("Failed to save output to file")
                return {"error": "Failed to save output to file"}
        except Exception as e:
            logger.error(f"Error saving output to file: {str(e)}")
            return {"error": f"Error saving output to file: {str(e)}"}
    else:
        # Format for display
        display_output = format_for_display(formatted_result, format_type)
        
        return {
            "output_type": "console",
            "output": display_output,
            "format": format_type,
            "result": formatted_result
        }

# CLI interface using Click
@click.command()
@click.option('--input', '-i', help='Direct text input')
@click.option('--input_file', '-f', help='Path to input file')
@click.option('--input_directory', '-d', help='Path to input directory')
@click.option('--file_pattern', default='*.txt', help='File pattern for directory input (default: *.txt)')
@click.option('--recursive', is_flag=True, help='Search recursively in subdirectories')
@click.option('--processing_strategy', type=click.Choice(['individual', 'concatenate']), 
              default='individual', help='How to process directory files (default: individual)')
@click.option('--output_file', '-o', help='Path to output file')
@click.option('--model', '-m', type=click.Choice(['chatgpt', 'claude', 'web_search']), default='chatgpt',
              help='AI model to use (default: chatgpt)')
@click.option('--format', '-fmt', type=click.Choice(['text', 'json', 'markdown', 'html']), 
              default='text', help='Output format (default: text)')
@click.option('--config', '-c', help='Path to workflow configuration file')
@click.option('--web_search', '-ws', help='Web search query (overrides other input methods)')
def cli(input: Optional[str], input_file: Optional[str], input_directory: Optional[str],
        file_pattern: str, recursive: bool, processing_strategy: str,
        output_file: Optional[str], model: str, format: str, config: Optional[str],
        web_search: Optional[str]):
    """Run the AI workflow from the command line."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger = logging.getLogger(__name__)
        
        # Check if a configuration file is provided
        if config:
            # Import config_workflow here to avoid circular imports
            try:
                from src.config_workflow import load_config, run_configurable_workflow
            except ModuleNotFoundError:
                from config_workflow import load_config, run_configurable_workflow
                
            logger.info(f"Loading workflow configuration from: {config}")
            workflow_config = load_config(config)
            
            if "error" in workflow_config:
                logger.error(f"Error loading configuration: {workflow_config['error']}")
                sys.exit(1)
            
            # Run configurable workflow
            result = run_configurable_workflow(
                workflow_config,
                input_text=input,
                input_file=input_file,
                input_directory=input_directory,
                file_pattern=file_pattern,
                recursive=recursive,
                processing_strategy=processing_strategy,
                output_file=output_file,
                format_type=format,
                web_search=web_search
            )
        else:
            # Run standard workflow
            result = run_workflow(
                input_text=input,
                input_file=input_file,
                input_directory=input_directory,
                file_pattern=file_pattern,
                recursive=recursive,
                processing_strategy=processing_strategy,
                model=model,
                output_file=output_file,
                format_type=format,
                web_search=web_search
            )
        
        # Check for errors
        if "error" in result:
            logger.error(f"Workflow error: {result['error']}")
            sys.exit(1)
        
        # Print output if not saved to file
        if result.get("output_type") == "console" and "output" in result:
            print(result["output"])
            
        logger.info("Workflow completed successfully")
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Run the CLI if this file is executed directly
    cli() 