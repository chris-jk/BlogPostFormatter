import os
import json
import webbrowser  # Add this import at the top
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

# Constants
CONFIG_FILE = "config.json"
PROMPT_FILE = "prompt.txt"
OPENAI_API_KEY_URL = "https://platform.openai.com/api-keys"

# Default settings
DEFAULT_MODEL = "gpt-4"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 4000
DEFAULT_PROMPT = "Format the following transcript into a structured blog post with a title, summary, and headings."

# Preferred voice IDs - based on your selection
PREFERRED_VOICE_IDS = [
    "14", "30", "38", "39", "66", "80", "89", "90", "97", "108"
]

def load_settings():
    """Load settings from the config file or return defaults"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return {
                    'api_key': config.get('api_key', ''),
                    'model': config.get('model', DEFAULT_MODEL),
                    'temperature': config.get('temperature', DEFAULT_TEMPERATURE),
                    'max_tokens': config.get('max_tokens', DEFAULT_MAX_TOKENS),
                    'preferred_voices': config.get('preferred_voices', PREFERRED_VOICE_IDS),
                    'last_voice_id': config.get('last_voice_id', '')
                }
    except Exception as e:
        print(f"Error loading settings: {str(e)}")
    
    # Return defaults if loading fails
    return {
        'api_key': '',
        'model': DEFAULT_MODEL,
        'temperature': DEFAULT_TEMPERATURE,
        'max_tokens': DEFAULT_MAX_TOKENS,
        'preferred_voices': PREFERRED_VOICE_IDS,
        'last_voice_id': ''
    }

def save_settings(settings):
    """Save settings to the config file"""
    try:
        # Ensure we maintain any existing settings
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    existing_settings = json.load(f)
                    # Update existing settings with new values
                    for key, value in settings.items():
                        existing_settings[key] = value
                    settings = existing_settings
            except:
                pass  # If reading fails, use the provided settings
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump(settings, f)
        return True
    except Exception as e:
        print(f"Error saving settings: {str(e)}")
        return False

def load_prompt():
    """Load the prompt from the file or return the default"""
    try:
        if os.path.exists(PROMPT_FILE):
            with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
                return f.read().strip()
        else:
            # Create the prompt file with default prompt if it doesn't exist
            with open(PROMPT_FILE, 'w', encoding='utf-8') as f:
                f.write(DEFAULT_PROMPT)
            return DEFAULT_PROMPT
    except Exception as e:
        print(f"Failed to load prompt file: {str(e)}")
        return DEFAULT_PROMPT

def save_preferred_voice(voice_id):
    """Save a voice ID to the preferred voices list"""
    try:
        settings = load_settings()
        
        # Initialize preferred_voices list if it doesn't exist
        if 'preferred_voices' not in settings:
            settings['preferred_voices'] = []
            
        # Add voice ID if not already in the list
        if voice_id not in settings['preferred_voices']:
            settings['preferred_voices'].append(voice_id)
            
        if save_settings(settings):
            return True
        return False
    except Exception as e:
        print(f"Error saving preferred voice: {str(e)}")
        return False

def remove_preferred_voice(voice_id):
    """Remove a voice ID from the preferred voices list"""
    try:
        settings = load_settings()
        
        # Check if preferred_voices exists and voice_id is in it
        if 'preferred_voices' in settings and voice_id in settings['preferred_voices']:
            settings['preferred_voices'].remove(voice_id)
            
        if save_settings(settings):
            return True
        return False
    except Exception as e:
        print(f"Error removing preferred voice: {str(e)}")
        return False

def get_preferred_voices():
    """Get the list of preferred voice IDs"""
    try:
        settings = load_settings()
        return settings.get('preferred_voices', PREFERRED_VOICE_IDS)
    except Exception:
        return PREFERRED_VOICE_IDS

def open_api_key_website():
    """Open the OpenAI API key website in the default browser"""
    try:
        webbrowser.open(OPENAI_API_KEY_URL)
        return True
    except Exception as e:
        print(f"Error opening API key website: {str(e)}")
        return False

def show_api_key_help():
    """Show a popup with OpenAI API key information and link"""
    result = messagebox.askquestion(
        "OpenAI API Key",
        "Would you like to open the OpenAI API key website?\n\n" +
        "You can create or manage your API keys there.",
        icon='info'
    )
    if result == 'yes':
        open_api_key_website()

def get_api_key():
    """Show a dialog to get the OpenAI API key with a help link"""
    dialog = tk.Toplevel()
    dialog.title("OpenAI API Key")
    dialog.geometry("400x150")
    dialog.transient(tk._default_root)
    dialog.grab_set()
    
    # Create and pack widgets
    label = ttk.Label(dialog, text="Enter your OpenAI API Key:")
    label.pack(pady=10)
    
    entry = ttk.Entry(dialog, width=40)
    entry.pack(pady=5)
    
    # Create a link to the API website
    link = ttk.Label(dialog, text="Get API Key", foreground="blue", cursor="hand2")
    link.pack(pady=5)
    link.bind("<Button-1>", lambda e: open_api_key_website())
    
    # Button frame
    button_frame = ttk.Frame(dialog)
    button_frame.pack(pady=10)
    
    api_key = ['']  # Use list to store the result
    
    def on_ok():
        api_key[0] = entry.get().strip()
        dialog.destroy()
    
    def on_cancel():
        dialog.destroy()
    
    ok_button = ttk.Button(button_frame, text="OK", command=on_ok)
    ok_button.pack(side=tk.LEFT, padx=5)
    
    cancel_button = ttk.Button(button_frame, text="Cancel", command=on_cancel)
    cancel_button.pack(side=tk.LEFT, padx=5)
    
    # Center the dialog
    dialog.update_idletasks()
    width = dialog.winfo_width()
    height = dialog.winfo_height()
    x = (dialog.winfo_screenwidth() // 2) - (width // 2)
    y = (dialog.winfo_screenheight() // 2) - (height // 2)
    dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    dialog.wait_window()
    return api_key[0]