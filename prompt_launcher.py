import PySimpleGUI as sg
import json
import webbrowser
import urllib.parse

# --- Configuration ---
PROMPTS_FILE = '/home/dan/Scripts/prompts.json'
DEFAULT_SEARCH_URL = 'https://chat.openai.com/?q='

# taille de la fenêtre
width, height = 800, 400  # remplace par la taille que tu veux

# taille de l'écran
screen_width, screen_height = sg.Window.get_screen_size()

# calcul pour centrer
x = (screen_width - width) // 2
y = (screen_height - height) // 2
# --- Helper Functions ---

def load_prompts(filename):
    """Loads prompts from a JSON file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # If the file doesn't exist, create it with an example prompt
        initial_prompts = {"Example Prompt": "This is an example. Replace it or add your own prompts."}
        save_prompts(filename, initial_prompts)
        return initial_prompts
    except json.JSONDecodeError:
        return {"Error": f"Could not decode JSON from {filename}"}

# --- NEW: Function to save prompts ---
def save_prompts(filename, prompts):
    """Saves the prompts dictionary to the JSON file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            # ensure_ascii=False handles special characters, indent=2 makes it readable
            json.dump(prompts, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        sg.popup_error(f"Error saving prompts to {filename}:\n{e}")
        return False

# --- NEW: Function to handle the 'Add Prompt' window ---
def add_prompt_window():
    """
    Creates and displays a modal window to add a new prompt.
    Returns a tuple (prompt_name, prompt_text) or None if canceled.
    """
    layout = [
        [sg.Text("Prompt Name (Key):")],
        [sg.Input(key='-PROMPT_NAME-', expand_x=True)],
        [sg.Text("Prompt Context (Value):")],
        [sg.Multiline(size=(60, 15), key='-PROMPT_TEXT-', expand_x=True, expand_y=True)],
        [sg.Button("Save", key='-SAVE-'), sg.Button("Cancel")]
    ]
    
    # 'modal=True' makes this window block the main window until it's closed
    window = sg.Window("Add New Prompt", layout, resizable=True,
    location=(x, y))
    
    new_prompt_data = None
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Cancel':
            break
        if event == '-SAVE-':
            prompt_name = values['-PROMPT_NAME-'].strip()
            prompt_text = values['-PROMPT_TEXT-'].strip()
            
            # Basic validation
            if not prompt_name:
                sg.popup_error("Prompt name cannot be empty.")
                continue
            if not prompt_text:
                sg.popup_error("Prompt context cannot be empty.")
                continue
            
            new_prompt_data = (prompt_name, prompt_text)
            break
            
    window.close()
    return new_prompt_data

# --- NEW: Function to handle the 'Edit Prompt' window ---
def edit_prompt_window(prompt_name, prompt_text):
    """
    Creates and displays a modal window to edit an existing prompt.
    Returns a tuple (new_prompt_name, new_prompt_text) or None if canceled.
    """
    layout = [
        [sg.Text("Prompt Name (Key):")],
        [sg.Input(prompt_name, key='-PROMPT_NAME-', expand_x=True)],
        [sg.Text("Prompt Context (Value):")],
        [sg.Multiline(prompt_text, size=(60, 15), key='-PROMPT_TEXT-', expand_x=True, expand_y=True)],
        [sg.Button("Save", key='-SAVE-'), sg.Button("Cancel")]
    ]
    
    window = sg.Window("Edit Prompt", layout, resizable=True,
    location=(x, y))
    
    edited_prompt_data = None
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Cancel':
            break
        if event == '-SAVE-':
            new_prompt_name = values['-PROMPT_NAME-'].strip()
            new_prompt_text = values['-PROMPT_TEXT-'].strip()
            
            if not new_prompt_name:
                sg.popup_error("Prompt name cannot be empty.")
                continue
            if not new_prompt_text:
                sg.popup_error("Prompt context cannot be empty.")
                continue
            
            edited_prompt_data = (new_prompt_name, new_prompt_text)
            break
            
    window.close()
    return edited_prompt_data

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
        # --- MODIFIED: Added 'Add', 'Edit', and 'Delete' buttons ---
        [sg.Button("Launch", key='-LAUNCH-'), sg.Button("Add Prompt", key='-ADD-'), sg.Button("Edit Prompt", key='-EDIT-'), sg.Button("Delete Prompt", key='-DELETE-'), sg.Button("Exit")]
    ]

    # Create the Window
    window = sg.Window('PromptLauncher V1', layout, resizable=True,
    location=(x, y))

    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        
        # If user closes window or clicks exit
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        
        # --- NEW: Event handler for the 'Add Prompt' button ---
        if event == '-ADD-':
            new_prompt = add_prompt_window()
            if new_prompt:
                prompt_name, prompt_text = new_prompt
                
                # Check if prompt already exists and ask for confirmation to overwrite
                if prompt_name in prompts:
                    if sg.popup_yes_no(f"Prompt '{prompt_name}' already exists. Overwrite it?") != 'Yes':
                        continue
                
                # Add or update the prompt in the dictionary
                prompts[prompt_name] = prompt_text
                
                # Save the updated dictionary back to the JSON file
                if save_prompts(PROMPTS_FILE, prompts):
                    # Update the dropdown list in the UI immediately
                    prompt_names = list(prompts.keys())
                    window['-PROMPT_CHOICE-'].update(values=prompt_names, value=prompt_name)

        # --- NEW: Event handler for the 'Edit Prompt' button ---
        if event == '-EDIT-':
            selected_prompt_name = values['-PROMPT_CHOICE-']
            if not selected_prompt_name or selected_prompt_name == "Error":
                sg.popup_error("Please select a prompt to edit.")
                continue

            prompt_text = prompts.get(selected_prompt_name, "")
            edited_prompt = edit_prompt_window(selected_prompt_name, prompt_text)

            if edited_prompt:
                new_prompt_name, new_prompt_text = edited_prompt
                
                # If the name has changed, remove the old prompt
                if new_prompt_name != selected_prompt_name:
                    del prompts[selected_prompt_name]
                
                prompts[new_prompt_name] = new_prompt_text
                
                if save_prompts(PROMPTS_FILE, prompts):
                    prompt_names = list(prompts.keys())
                    window['-PROMPT_CHOICE-'].update(values=prompt_names, value=new_prompt_name)

        # --- NEW: Event handler for the 'Delete Prompt' button ---
        if event == '-DELETE-':
            selected_prompt_name = values['-PROMPT_CHOICE-']
            if not selected_prompt_name or selected_prompt_name == "Error":
                sg.popup_error("Please select a prompt to delete.")
                continue
            
            if sg.popup_yes_no(f"Are you sure you want to delete the prompt '{selected_prompt_name}'?") == 'Yes':
                del prompts[selected_prompt_name]
                
                if save_prompts(PROMPTS_FILE, prompts):
                    prompt_names = list(prompts.keys())
                    # Update dropdown to the first available prompt or an empty string
                    new_selection = prompt_names[0] if prompt_names else ''
                    window['-PROMPT_CHOICE-'].update(values=prompt_names, value=new_selection)

        # If user clicks the Launch button (existing functionality)
        if event == '-LAUNCH-':
            selected_prompt_name = values['-PROMPT_CHOICE-']
            question = values['-QUESTION-']
            
            if selected_prompt_name and selected_prompt_name != "Error":
                pre_prompt = prompts.get(selected_prompt_name, "")
                combined_text = f"voici le context: \n\n{pre_prompt}\n\nma question est: \n\n{question}"
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
