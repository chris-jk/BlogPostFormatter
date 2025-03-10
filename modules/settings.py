import os
import json

# Constants
CONFIG_FILE = "config.json"
PROMPT_FILE = "prompt.txt"

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