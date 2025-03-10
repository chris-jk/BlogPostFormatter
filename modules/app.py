import os
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk, messagebox
import threading
import openai

# Fix the import statement
from modules.settings import (
    load_settings, save_settings, load_prompt, 
    PREFERRED_VOICE_IDS, DEFAULT_MODEL, DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS
)

# Update the imports at the top of the file
from modules.tts import (
    speak_text, stop_text_to_speech, test_voices, select_voice, initialize_engine
)

from modules.openai_api import (
    get_api_key, set_new_api_key, generate_blog_post
)

# Available OpenAI models
AVAILABLE_MODELS = [
    "gpt-4",
    "gpt-4-turbo",
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-16k"
]

# Help text definitions
MODEL_HELP = """
Available AI Models:

• gpt-4: Most powerful model with highest quality results, but slower and more expensive.
  Best for: Complex formatting, nuanced understanding, professional content.

• gpt-4-turbo: Faster version of GPT-4 with similar quality but improved performance.
  Best for: Balance of quality and speed.

• gpt-3.5-turbo: Faster and more economical model with good quality for most tasks.
  Best for: Quick drafts, simpler content, or when speed is important.

• gpt-3.5-turbo-16k: Similar to gpt-3.5-turbo but with larger context window.
  Best for: Processing longer transcripts that might exceed standard limits.
"""

TEMPERATURE_HELP = """
Temperature controls the randomness or creativity of the output:
• Low temperature (0.1-0.3): 
  - More focused, deterministic responses
  - Consistent, predictable formatting
  - Less creative but more accurate
  - Better for factual, technical content
  - Good for maintaining specific structure

• Medium temperature (0.4-0.7):
  - Balanced creativity and coherence
  - Good default for most blog posts
  - Adds some variation while staying on topic
  
• High temperature (0.8-1.0):
  - More creative, diverse outputs
  - Introduces more variation and personality
  - Can generate more engaging, unique phrasing
  - Better for creative writing, casual blogs
  - May occasionally stray from conventional formats

Recommended: 0.7 for general blog posts, 0.3-0.5 for technical/factual content.
"""

MAX_TOKENS_HELP = """
Max Tokens controls the maximum length of the generated blog post:

• 1000-2000 tokens: 
  - Short blog posts (about 750-1500 words)
  - More concise summaries
  - Faster generation time

• 3000-5000 tokens:
  - Medium-length posts (about 2250-3750 words)
  - Good balance of detail and brevity
  - Standard for most blog content

• 6000-8000 tokens:
  - Longer, more detailed posts (about 4500-6000 words)
  - In-depth exploration of topics
  - Comprehensive coverage

Note: A token is approximately 3/4 of a word in English.
The model may not use all available tokens if it completes the post earlier.
"""

# Global variables for UI components
output_text = None
progress_bar = None
select_button = None
api_status = None
tts_engine = None  # Add this global variable
speech_status = None  # Add global status label

# Add to imports at the top
import time

# Update global variables
global output_text, progress_bar, select_button, api_status, tts_engine, speech_status

def create_ui(root):
    """Create the complete UI for the application"""
    global output_text, progress_bar, select_button, api_status, tts_engine, speech_status
    
    # Get saved settings
    settings = load_settings()

    # Create Tkinter variables
    model_var = tk.StringVar(value=settings.get('model', DEFAULT_MODEL))
    selection_var = tk.StringVar(value="folder")
    tts_var = tk.StringVar(value="offline")
    
    # --- API KEY SECTION ---
    api_frame = ttk.Frame(root, padding=10)
    api_frame.pack(fill=tk.X)
    
    api_button = ttk.Button(api_frame, text="Change API Key", 
                           command=lambda: set_new_api_key(api_status))
    api_button.pack(side=tk.LEFT, padx=5)
    
    api_status = ttk.Label(api_frame, text="API Key: Not set")
    api_status.pack(side=tk.LEFT, padx=5)
    
    prompt_button = ttk.Button(api_frame, text="Edit Prompt", command=edit_prompt)
    prompt_button.pack(side=tk.RIGHT, padx=5)
    
    # --- MODEL SETTINGS SECTION ---
    model_frame = ttk.LabelFrame(root, text="Model Settings", padding=10)
    model_frame.pack(fill=tk.X, padx=10, pady=5)
    
    # Model dropdown
    model_row = ttk.Frame(model_frame)
    model_row.grid(row=0, column=0, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
    
    model_label = ttk.Label(model_row, text="Model:", width=15)
    model_label.pack(side=tk.LEFT)
    
    model_dropdown = ttk.Combobox(model_row, textvariable=model_var, values=AVAILABLE_MODELS, 
                                 state="readonly", width=20)
    model_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    model_help_btn = ttk.Button(model_row, text="?", width=3, 
                               command=lambda: show_help(root, "Model Selection Help", MODEL_HELP))
    model_help_btn.pack(side=tk.LEFT, padx=5)
    
    # Temperature slider
    temp_row = ttk.Frame(model_frame)
    temp_row.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
    
    temp_label = ttk.Label(temp_row, text="Temperature:", width=15)
    temp_label.pack(side=tk.LEFT)
    
    temp_frame = ttk.Frame(temp_row)
    temp_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    temp_scale = ttk.Scale(temp_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL)
    temp_scale.set(settings.get('temperature', DEFAULT_TEMPERATURE))
    temp_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    temp_value = ttk.Label(temp_frame, text=str(settings.get('temperature', DEFAULT_TEMPERATURE)), width=5)
    temp_value.pack(side=tk.LEFT)
    
    temp_help_btn = ttk.Button(temp_row, text="?", width=3,
                              command=lambda: show_help(root, "Temperature Help", TEMPERATURE_HELP))
    temp_help_btn.pack(side=tk.LEFT, padx=5)
    
    temp_desc_label = ttk.Label(model_frame, text="(Balanced)")
    temp_desc_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=20, pady=0)
    
    # Max tokens slider
    token_row = ttk.Frame(model_frame)
    token_row.grid(row=3, column=0, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
    
    token_label = ttk.Label(token_row, text="Max Tokens:", width=15)
    token_label.pack(side=tk.LEFT)
    
    token_frame = ttk.Frame(token_row)
    token_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    token_scale = ttk.Scale(token_frame, from_=1000, to=8000, orient=tk.HORIZONTAL)
    token_scale.set(settings.get('max_tokens', DEFAULT_MAX_TOKENS))
    token_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    token_value = ttk.Label(token_frame, text=str(settings.get('max_tokens', DEFAULT_MAX_TOKENS)), width=5)
    token_value.pack(side=tk.LEFT)
    
    token_help_btn = ttk.Button(token_row, text="?", width=3,
                               command=lambda: show_help(root, "Max Tokens Help", MAX_TOKENS_HELP))
    token_help_btn.pack(side=tk.LEFT, padx=5)
    
    token_desc_label = ttk.Label(model_frame, text="(Medium Post)")
    token_desc_label.grid(row=4, column=0, columnspan=2, sticky=tk.W, padx=20, pady=0)
    
    # Save settings button
    save_settings_button = ttk.Button(model_frame, text="Save Settings",
                                     command=lambda: save_model_settings(model_var, temp_scale, token_scale))
    save_settings_button.grid(row=5, column=0, columnspan=2, sticky=tk.E, padx=5, pady=10)
    
    # --- SELECTION OPTIONS SECTION ---
    selection_frame = ttk.Frame(root, padding=10)
    selection_frame.pack(fill=tk.X)
    
    # Radio buttons for selection type
    ttk.Radiobutton(selection_frame, text="Process Single File", 
                   variable=selection_var, value="file").pack(side=tk.LEFT, padx=5)
    ttk.Radiobutton(selection_frame, text="Process Folder", 
                   variable=selection_var, value="folder").pack(side=tk.LEFT, padx=5)
    
    # Select button
    select_button = ttk.Button(selection_frame, text="Select", 
                              command=lambda: process_selection(root, selection_var, model_var, temp_scale, token_scale))
    select_button.pack(side=tk.LEFT, padx=20)
    
    # --- PROGRESS BAR SECTION ---
    progress_frame = ttk.Frame(root, padding=(10, 0))
    progress_frame.pack(fill=tk.X)
    
    # Progress bar (initially hidden)
    progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate")
    
    # --- OUTPUT AREA SECTION ---
    output_frame = ttk.Frame(root, padding=5)
    output_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    
    # Output text area
    output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, width=100, height=20)  # Changed height from 30 to 20
    output_text.pack(fill=tk.BOTH, expand=True)
    
    # --- BOTTOM BUTTONS SECTION ---
    button_frame = ttk.Frame(output_frame, padding=(0, 5, 0, 0))
    button_frame.pack(fill=tk.X)
    
    # TTS Method Selection
    tts_frame = ttk.Frame(button_frame)
    tts_frame.pack(side=tk.LEFT, padx=10)
    
    tts_label = ttk.Label(tts_frame, text="TTS Method:")
    tts_label.pack(side=tk.LEFT, padx=(0,5))
    
    offline_radio = ttk.Radiobutton(tts_frame, text="Offline", variable=tts_var, value="offline")
    offline_radio.pack(side=tk.LEFT, padx=5)
    
    online_radio = ttk.Radiobutton(tts_frame, text="Online", variable=tts_var, value="online")
    online_radio.pack(side=tk.LEFT)
    
    # Voice Manager button
    voice_manager_btn = ttk.Button(tts_frame, text="Voice Manager", 
                                 command=lambda: manage_voice(root, tts_var))
    voice_manager_btn.pack(side=tk.LEFT, padx=10)
    
    # Speak button
    speak_button = ttk.Button(button_frame, text="Speak", 
                             command=lambda: simple_speak_text(root, output_text, tts_var))
    speak_button.pack(side=tk.LEFT, padx=10)
    
    # Copy button
    copy_button = ttk.Button(button_frame, text="Copy to Clipboard", 
                            command=lambda: copy_to_clipboard(root, output_text))
    copy_button.pack(side=tk.RIGHT)
    
    # Stop button with enhanced error handling
    stop_button = ttk.Button(button_frame, text="Stop", 
                            command=lambda: safe_stop_speech())
    stop_button.pack(side=tk.LEFT, padx=10)
    
    # After the stop button definition, add:
    speech_status = ttk.Label(button_frame, text="Status: Ready")
    speech_status.pack(side=tk.LEFT, padx=10)
    
    # ... rest of the UI creation ...
    
    # At the end of create_ui, add TTS initialization:
    try:
        tts_engine = initialize_engine()
        if tts_engine:
            voice_id = settings.get('voice_id', '')
            if voice_id:
                try:
                    tts_engine.setProperty('voice', voice_id)
                    print(f"Initial voice set to: {voice_id}")
                except Exception as e:
                    print(f"Warning: Could not set initial voice: {e}")
        else:
            print("Warning: TTS engine initialization failed on startup")
    except Exception as e:
        print(f"Error initializing TTS engine at startup: {e}")

def manage_voice(root, tts_var):
    """Open the voice management dialog"""
    if tts_var.get() == "offline":
        try:
            select_voice(root, tts_var)
        except Exception as e:
            print(f"Error in manage_voice: {e}")
            messagebox.showerror("Error", f"Failed to select voice: {str(e)}")
    else:
        messagebox.showinfo("Online TTS", "Voice selection is not available for online TTS.")

def simple_speak_text(root, output_text, tts_var):
    """Simplified speak text function with improved error handling"""
    global speech_status
    
    try:
        # Get text from output area
        text = output_text.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "No text to speak!")
            return
        
        # Update status
        if speech_status:
            speech_status.config(text="Status: Starting speech...")
            # Force UI update
            root.update_idletasks()
        
        # Create dummy variable for test_all_voices parameter
        class DummyVar:
            def get(self):
                return False
        
        dummy_var = DummyVar()
        
        # Check if already speaking
        from modules.tts import is_speaking
        
        if is_speaking:
            # First try to stop any ongoing speech
            if speech_status:
                speech_status.config(text="Status: Stopping previous speech...")
                # Force UI update
                root.update_idletasks()
            try:
                stop_text_to_speech()
                time.sleep(0.5)  # Give it a moment to stop
            except Exception as e:
                print(f"Warning: Couldn't stop existing speech: {e}")
        
        # Now speak the text using the imported function
        speak_text(root, output_text, tts_var, dummy_var)
        
    except Exception as e:
        print(f"Error in simple_speak_text: {e}")
        if speech_status:
            speech_status.config(text=f"Status: Error - {str(e)[:30]}...")
        messagebox.showerror("Speech Error", f"Failed to start speech: {str(e)}")

        
def safe_stop_speech():
    """Safely stop the text-to-speech with status updates"""
    global speech_status
    
    if speech_status:
        speech_status.config(text="Status: Stopping speech...")
    
    try:
        print("Attempting to stop speech...")
        result = stop_text_to_speech()
        print(f"Stop speech result: {result}")
        if speech_status:
            speech_status.config(text="Status: Speech stopped")
    except Exception as e:
        print(f"Error stopping speech: {str(e)}")
        if speech_status:
            speech_status.config(text=f"Status: Error stopping - {str(e)[:30]}...")
        messagebox.showerror("Error", f"Error stopping speech: {str(e)}")
    finally:
        try:
            root.update_idletasks()
        except Exception as e:
            print(f"Error updating UI: {e}")

def main():
    root = tk.Tk()
    root.title("AI Blog Post Generator")
    root.geometry("800x600")
    
    def on_closing():
        try:
            safe_stop_speech()
            global tts_engine
            if tts_engine:
                try:
                    del tts_engine
                except:
                    pass
        except:
            pass
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    create_ui(root)
    root.mainloop()

if __name__ == "__main__":
    main()