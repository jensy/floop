# AI Workflow MVP

This project is a Minimum Viable Product (MVP) that orchestrates interactions between multiple AI models (OpenAI's ChatGPT and Anthropic's Claude) in a modular workflow. It allows users to leverage multiple Large Language Models (LLMs) in a coordinated pipeline for complex tasks on their local environment, ensuring control, flexibility, and privacy.

## Features

- **Multiple AI Model Support**: Interact with both OpenAI's ChatGPT and Anthropic's Claude.
- **Flexible Input Handling**: Process input from direct text or files.
- **Multi-Step Workflows**: Chain AI models together (e.g., Claude → ChatGPT).
- **Error Handling**: Robust error handling with retry logic for temporary failures.
- **Output Formatting**: Clean and format AI responses for better readability.
- **Command-Line Interface**: Easy-to-use CLI with various options.

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

# Save output to a file
ai-workflow --input "Tell me a joke" --output_file joke.txt

# Format output as markdown
ai-workflow --input "Explain AI" --format markdown
```

### Command-Line Options

- `--input`, `-i`: Direct text input
- `--input_file`, `-f`: Path to input file
- `--use_chatgpt`: Use ChatGPT model
- `--use_claude`: Use Claude model
- `--model`, `-m`: AI model to use (chatgpt, claude, claude-first)
- `--max_tokens`: Maximum tokens in response (default: 1000)
- `--temperature`: Temperature (randomness) (default: 0.7)
- `--output_file`, `-o`: Path to output file
- `--format`: Output format (text, markdown)

## Project Structure

- `src/`: Source code directory
  - `chatgpt_client.py`: OpenAI (ChatGPT) API client
  - `claude_client.py`: Anthropic (Claude) API client
  - `input_handler.py`: Input handling functions
  - `workflow.py`: Workflow orchestrator
  - `output_formatter.py`: Output formatting functions
- `ai_workflow.py`: Main entry point
- `setup.py`: Package setup script
- `.env`: Environment variables (API keys)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [OpenAI](https://openai.com/) for the ChatGPT API
- [Anthropic](https://www.anthropic.com/) for the Claude API 