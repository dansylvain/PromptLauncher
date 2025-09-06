import PySimpleGUI as sg
import json
import webbrowser
import urllib.parse

# --- Configuration ---
PROMPTS_FILE = '/home/dan/Scripts/prompts.json'
DEFAULT_SEARCH_URL = 'https://chat.openai.com/?q='

# --- Helper Functions ---

def load_prompts(filename):
    """Loads prompts from a JSON file."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"Error": f"Prompts file not found: {filename}"}
    except json.JSONDecodeError:
        return {"Error": f"Could not decode JSON from {filename}"}

# --- Main Application Logic ---

def main():
    """Main function to run the PromptLauncher application."""
    
    prompts = load_prompts(PROMPTS_FILE)
    prompt_names = list(prompts.keys())

    # Define the window's layout
    layout = [
        [sg.Text("Select a Pre-prompt:")],
        [sg.Combo(prompt_names, default_value=prompt_names[0] if prompt_names else '', key='-PROMPT_CHOICE-', readonly=True, expand_x=True)],
        [sg.Text("Enter your question or prompt:")],
        [sg.Multiline(size=(80, 10), key='-QUESTION-', expand_x=True, expand_y=True)],
        [sg.Button("Launch", key='-LAUNCH-'), sg.Button("Exit")]
    ]

    # Create the Window
    window = sg.Window('PromptLauncher', layout, resizable=True)

    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        
        # If user closes window or clicks exit
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        
        # If user clicks the Launch button
        if event == '-LAUNCH-':
            selected_prompt_name = values['-PROMPT_CHOICE-']
            question = values['-QUESTION-']
            
            if selected_prompt_name and selected_prompt_name != "Error":
                pre_prompt = prompts[selected_prompt_name]
                combined_text = f"{pre_prompt}\n\n{question}"
            else:
                combined_text = question

            if not combined_text.strip():
                sg.popup_error("The prompt cannot be empty.")
                continue

            # URL-encode the combined text
            encoded_text = urllib.parse.quote_plus(combined_text)
            
            # Open the browser with the combined text
            webbrowser.open(f"{DEFAULT_SEARCH_URL}{encoded_text}", new=2)

    window.close()

if __name__ == '__main__':
    main()
