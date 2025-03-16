# AI Workflow MVP

This project is a Minimum Viable Product (MVP) that orchestrates interactions between multiple AI models (OpenAI's ChatGPT and Anthropic's Claude) in a modular workflow. It allows users to leverage multiple Large Language Models (LLMs) in a coordinated pipeline for complex tasks on their local environment, ensuring control, flexibility, and privacy.

## Features

- **Multiple AI Model Support**: Interact with both OpenAI's ChatGPT and Anthropic's Claude.
- **Flexible Input Handling**: Process input from direct text, files, or directories.
- **Multi-Step Workflows**: Chain AI models together (e.g., Claude → ChatGPT).
- **Configurable Workflows**: Define custom workflows using JSON configuration files.
- **Error Handling**: Robust error handling with retry logic for temporary failures.
- **Output Formatting**: Clean and format AI responses for better readability.
- **Command-Line Interface**: Easy-to-use CLI with various options.
- **Directory Processing**: Process multiple files in a directory with individual or concatenated strategies.

## Installation

### Prerequisites

- Python 3.6 or higher
- OpenAI API key
- Anthropic API key

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-workflow-mvp.git
   cd ai-workflow-mvp
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the package:
   ```bash
   pip install -e .
   ```

4. Create a `.env` file in the project root with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   ```

## Usage

### Basic Usage

```bash
# Use ChatGPT (default)
ai-workflow --input "Summarize this: The AI workflow MVP is a system that orchestrates multiple AI model interactions."

# Use Claude
ai-workflow --input "Explain quantum physics in simple terms" --use_claude

# Multi-step workflow (Claude → ChatGPT)
ai-workflow --input "Analyze this text" --model claude-first

# Process input from a file
ai-workflow --input_file document.txt --use_chatgpt

# Process all text files in a directory (individually)
ai-workflow --input_directory data/ --file_pattern "*.txt" --recursive

# Process all text files in a directory (concatenated)
ai-workflow --input_directory data/ --processing_strategy concatenate

# Save output to a file
ai-workflow --input "Tell me a joke" --output_file joke.txt

# Format output as markdown
ai-workflow --input "Explain AI" --format markdown
```

### Configurable Workflows

You can define custom workflows using JSON configuration files:

```bash
# Run a workflow with a configuration file
ai-workflow --config configs/my_workflow.json

# Override configuration values with CLI arguments
ai-workflow --config configs/my_workflow.json --input "Custom input" --output_file custom_output.txt
```

#### Configuration File Format

```json
{
  "name": "Sample Multi-Step Workflow",
  "description": "A sample workflow that chains multiple AI models together",
  "input": {
    "type": "text",
    "value": "Analyze the impact of artificial intelligence on healthcare."
  },
  "steps": [
    {
      "name": "initial_analysis",
      "model": "claude",
      "model_params": {
        "model": "claude-3-sonnet-20240229",
        "max_tokens": 1000,
        "temperature": 0.7
      },
      "prompt_template": "{input}"
    },
    {
      "name": "refinement",
      "model": "chatgpt",
      "model_params": {
        "model": "gpt-3.5-turbo",
        "max_tokens": 1000,
        "temperature": 0.5
      },
      "prompt_template": "Refine and expand on this analysis: {initial_analysis.output}"
    }
  ],
  "output": {
    "type": "file",
    "path": "results/ai_healthcare_analysis.md",
    "format": "markdown"
  }
}
```

#### Directory Input Configuration

You can also configure workflows to process multiple files in a directory:

```json
{
  "name": "Directory Input Workflow",
  "description": "A workflow that processes all text files in a directory",
  "input": {
    "type": "directory",
    "path": "sample_data",
    "file_pattern": "*.txt",
    "recursive": true,
    "processing_strategy": "individual"
  },
  "steps": [
    {
      "name": "summarize",
      "model": "claude",
      "prompt_template": "Summarize the following text in 2-3 sentences: {{input}}"
    }
  ],
  "output": {
    "type": "file",
    "format": "markdown"
  }
}
```

The `processing_strategy` can be:
- `individual`: Process each file separately (returns multiple results)
- `concatenate`: Combine all files into a single input (returns a single result)

### Command-Line Options

- `--input`, `-i`: Direct text input
- `--input_file`, `-f`: Path to input file
- `--input_directory`, `-d`: Path to input directory
- `--file_pattern`: File pattern for directory input (default: *.txt)
- `--recursive`: Search recursively in subdirectories
- `--processing_strategy`: How to process directory files (individual or concatenate)
- `--use_chatgpt`: Use ChatGPT model
- `--use_claude`: Use Claude model
- `--model`, `-m`: AI model to use (chatgpt, claude, claude-first)
- `--max_tokens`: Maximum tokens in response (default: 1000)
- `--temperature`: Temperature (randomness) (default: 0.7)
- `--output_file`, `-o`: Path to output file
- `--format`: Output format (text, markdown)
- `--config`, `-c`: Path to workflow configuration file
- `--legacy-mode`: Run in legacy mode (ignore configuration)

## Project Structure

- `src/`: Source code directory
  - `chatgpt_client.py`: OpenAI (ChatGPT) API client
  - `claude_client.py`: Anthropic (Claude) API client
  - `input_handler.py`: Input handling functions
  - `workflow.py`: Legacy workflow orchestrator
  - `config_workflow.py`: Configurable workflow orchestrator
  - `output_formatter.py`: Output formatting functions
- `configs/`: Configuration files for workflows
- `ai_workflow.py`: Main entry point
- `setup.py`: Package setup script
- `.env`: Environment variables (API keys)

## Creating Custom Workflows

You can create custom workflows by defining a JSON configuration file with the following components:

1. **Input**: Specify the input source (text or file)
2. **Steps**: Define a sequence of steps, each with a model, parameters, and prompt template
3. **Output**: Specify the output destination (console or file) and format

### Prompt Templates

Prompt templates can reference:
- The original input: `{input}`
- Output from previous steps: `{step_name.output}`

For example:
```json
"prompt_template": "Summarize this analysis: {analysis.output}"
```

### Example Workflows

Several example workflows are provided in the `configs/` directory:
- `example.json`: Simple workflow with a single step
- `file_input_example.json`: Workflow that reads input from a file
- `file_output_example.json`: Workflow that writes output to a file
- `workflow_config.json`: Multi-step workflow that chains multiple models

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [OpenAI](https://openai.com/) for the ChatGPT API
- [Anthropic](https://www.anthropic.com/) for the Claude API 