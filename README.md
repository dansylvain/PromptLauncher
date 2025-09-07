# PromptLauncher

## Description
This application helps initiate a conversation with a Large Language Model (LLM) by providing a predetermined context.

## Features
- Easily start conversations with an LLM
- Use predefined prompts for consistent context
- Simple user interface for selecting models and entering questions

## Installation
- Ensure the `prompts.json` file is present in the project directory.
- No additional installation steps required for basic usage.

## Desiderata
- error popup position could be set (to be tested, but how?)
- file prompts.json could be chosen from the disk, if not found


## Usage
1. Choose a preprompt model from the interface.
2. Enter your question.
3. Click "Launch" to start the conversation with the LLM.

## Project Structure
- `prompt_launcher.py`: Main application script
- `prompts.json`: Contains predefined prompts and contexts
- `build/`: Directory for build artifacts
- `README.md`: Project documentation
