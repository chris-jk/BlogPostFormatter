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

def create_ui(root):
    """Create the complete UI for the application"""
    # Create global variables that need to be accessed by functions
    global output_text, progress_bar, select_button, api_status, tts_engine
    
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
    
    # Stop button with error handling
    stop_button = ttk.Button(button_frame, text="Stop", 
                            command=lambda: safe_stop_speech())
    stop_button.pack(side=tk.LEFT, padx=10)
    
    # --- EVENT BINDINGS ---
    def update_temp_value(event):
        val = round(float(temp_scale.get()), 2)
        temp_value.config(text=str(val))
        
        # Update the temperature description label
        if val <= 0.3:
            temp_desc_label.config(text="(Focused, Factual)")
        elif val <= 0.7:
            temp_desc_label.config(text="(Balanced)")
        else:
            temp_desc_label.config(text="(Creative, Varied)")
    
    temp_scale.bind("<Motion>", update_temp_value)
    temp_scale.bind("<ButtonRelease-1>", update_temp_value)
    
    def update_token_value(event):
        val = int(token_scale.get())
        token_value.config(text=str(val))
        
        # Update the token description label
        if val <= 2000:
            token_desc_label.config(text="(Short Post)")
        elif val <= 5000:
            token_desc_label.config(text="(Medium Post)")
        else:
            token_desc_label.config(text="(Long Post)")
    
    token_scale.bind("<Motion>", update_token_value)
    token_scale.bind("<ButtonRelease-1>", update_token_value)
    
    # --- INITIALIZE API KEY ---
    api_key = settings.get('api_key', '')
    if api_key:
        openai.api_key = api_key
        api_status.config(text="API Key: Set ✓")
    else:
        openai.api_key = get_api_key()
        if openai.api_key:
            api_status.config(text="API Key: Set ✓")
    
    # Set the initial description labels based on loaded settings
    temp_val = settings.get('temperature', DEFAULT_TEMPERATURE)
    if temp_val <= 0.3:
        temp_desc_label.config(text="(Focused, Factual)")
    elif temp_val <= 0.7:
        temp_desc_label.config(text="(Balanced)")
    else:
        temp_desc_label.config(text="(Creative, Varied)")
    
    token_val = settings.get('max_tokens', DEFAULT_MAX_TOKENS)
    if token_val <= 2000:
        token_desc_label.config(text="(Short Post)")
    elif token_val <= 5000:
        token_desc_label.config(text="(Medium Post)")
    else:
        token_desc_label.config(text="(Long Post)")

def manage_voice(root, tts_var):
    """Open the voice management dialog"""
    if tts_var.get() == "offline":
        # Initialize a temporary engine for voice selection
        temp_engine = initialize_engine()
        if not temp_engine:
            messagebox.showerror("Error", "Failed to initialize speech engine.")
            return
            
        try:
            # Use select_voice instead of select_voice_dialog
            select_voice(root, tts_var)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to select voice: {str(e)}")
        finally:
            try:
                del temp_engine
            except:
                pass
    else:
        messagebox.showinfo("Online TTS", "Voice selection is not available for online TTS.")

def simple_speak_text(root, output_text, tts_var):
    """Simplified speak text function that doesn't use the test_all_voices parameter"""
    from modules.tts import speak_text as tts_speak_text
    
    # Get text from output area
    text = output_text.get(1.0, tk.END).strip()
    if not text:
        messagebox.showwarning("Warning", "No text to speak!")
        return
    
    # Create dummy variable for test_all_voices parameter
    class DummyVar:
        def get(self):
            return False
    
    dummy_var = DummyVar()
    tts_speak_text(root, output_text, tts_var, dummy_var)


def safe_stop_speech():
    """Safely stop the text-to-speech with error handling"""
    try:
        stop_text_to_speech()
    except Exception as e:
        print(f"Error stopping speech: {e}")
        messagebox.showerror("Error", f"Error stopping speech: {str(e)}")
    finally:
        # Ensure UI remains responsive
        root.update_idletasks()

def show_help(root, title, message):
    """Show a help window with the provided title and message"""
    help_window = tk.Toplevel(root)
    help_window.title(title)
    help_window.geometry("500x300")
    help_window.transient(root)  # Make window modal
    help_window.grab_set()
    
    # Create text widget with scrollbar
    help_frame = ttk.Frame(help_window, padding=10)
    help_frame.pack(fill=tk.BOTH, expand=True)
    
    help_text = scrolledtext.ScrolledText(help_frame, wrap=tk.WORD, width=60, height=15)
    help_text.pack(fill=tk.BOTH, expand=True)
    help_text.insert(tk.END, message)
    help_text.config(state=tk.DISABLED)  # Make read-only
    
    # Close button
    close_button = ttk.Button(help_window, text="Close", command=help_window.destroy)
    close_button.pack(pady=10)

def edit_prompt():
    """Open the prompt file in the default system editor"""
    try:
        # Make sure the prompt file exists
        prompt = load_prompt()  # This creates the file if it doesn't exist
        
        # Open the prompt file with the default system editor
        os.startfile("prompt.txt") if os.name == 'nt' else os.system(f'open "prompt.txt"')
        
        messagebox.showinfo("Edit Prompt", "The prompt file has been opened for editing.\n\nSave the file when you're done editing to use the updated prompt.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open prompt file: {str(e)}")

def save_model_settings(model_var, temp_scale, token_scale):
    """Save the current model settings"""
    try:
        settings = load_settings()
        settings['model'] = model_var.get()
        settings['temperature'] = float(temp_scale.get())
        settings['max_tokens'] = int(token_scale.get())
        
        if save_settings(settings):
            messagebox.showinfo("Success", "Settings saved successfully!")
        else:
            messagebox.showwarning("Warning", "Failed to save settings.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def process_selection(root, selection_var, model_var, temp_scale, token_scale):
    """Process the selected file or folder"""
    # Ensure we have an API key
    if not openai.api_key:
        openai.api_key = get_api_key()
        if not openai.api_key:
            return
        else:
            api_status.config(text="API Key: Set ✓")
    
    # Start processing in a separate thread
    threading.Thread(
        target=lambda: process_in_background(root, selection_var, model_var, temp_scale, token_scale), 
        daemon=True
    ).start()

def process_in_background(root, selection_var, model_var, temp_scale, token_scale):
    """Background thread for processing files"""
    # Enable the progress bar
    progress_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
    progress_bar.start(10)  # Start the indeterminate progress
    
    # Disable the select button during processing
    select_button.config(state=tk.DISABLED)
    
    try:
        if selection_var.get() == "file":
            process_file(root, model_var, temp_scale, token_scale)
        else:
            process_folder(root, model_var, temp_scale, token_scale)
    finally:
        # Hide the progress bar and re-enable the select button
        progress_bar.stop()
        progress_bar.grid_forget()
        select_button.config(state=tk.NORMAL)

def process_file(root, model_var, temp_scale, token_scale):
    """Process a single text file"""
    file_selected = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if not file_selected:
        return
    
    # Clear the output text area
    output_text.delete(1.0, tk.END)
    
    try:
        with open(file_selected, "r", encoding="utf-8") as file:
            transcript = file.read()
        
        # Get the current prompt
        prompt = load_prompt()
        
        # Show a "Processing..." message
        output_text.insert(tk.END, "Processing...\n\n")
        root.update_idletasks()
        
        # Get model settings
        model = model_var.get()
        temperature = float(temp_scale.get())
        max_tokens = int(token_scale.get())
        
        formatted_post = generate_blog_post(transcript, prompt, model, temperature, max_tokens)
        
        # Clear the "Processing..." message
        output_text.delete(1.0, tk.END)
        
        filename = os.path.basename(file_selected)
        output_text.insert(tk.END, f"=== {filename} ===\n\n" + formatted_post + "\n\n")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def process_folder(root, model_var, temp_scale, token_scale):
    """Process all text files in a selected folder"""
    folder_selected = filedialog.askdirectory()
    if not folder_selected:
        return
    
    # Clear the output text area
    output_text.delete(1.0, tk.END)
    
    try:
        # Get the current prompt
        prompt = load_prompt()
        
        # Get model settings
        model = model_var.get()
        temperature = float(temp_scale.get())
        max_tokens = int(token_scale.get())
        
        # Show a "Processing..." message
        output_text.insert(tk.END, "Processing files...\n\n")
        root.update_idletasks()
        
        # Count how many files to process
        txt_files = [f for f in os.listdir(folder_selected) if f.endswith(".txt")]
        total_files = len(txt_files)
        
        for i, filename in enumerate(txt_files):
            # Update processing status
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, f"Processing file {i+1} of {total_files}: {filename}...\n\n")
            root.update_idletasks()
            
            filepath = os.path.join(folder_selected, filename)
            with open(filepath, "r", encoding="utf-8") as file:
                transcript = file.read()
            
            formatted_post = generate_blog_post(transcript, prompt, model, temperature, max_tokens)
            
            # Clear and update the output area with all processed files
            output_text.delete(1.0, tk.END)
            for j, processed_file in enumerate(txt_files[:i+1]):
                if j == i:  # This is the file we just processed
                    output_text.insert(tk.END, f"=== {processed_file} ===\n\n" + formatted_post + "\n\n")
                else:
                    # Just indicate it was processed earlier
                    output_text.insert(tk.END, f"=== {processed_file} === (Processed)\n\n")
            
            root.update_idletasks()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def copy_to_clipboard(root, output_text):
    """Copy the contents of the output text area to the clipboard"""
    content = output_text.get(1.0, tk.END)
    root.clipboard_clear()
    root.clipboard_append(content)
    messagebox.showinfo("Success", "Content copied to clipboard!")

def safe_stop_speech():
    """Safely stop the text-to-speech with error handling"""
    try:
        # Use the imported function
        stop_text_to_speech()
    except Exception as e:
        print(f"Error stopping speech: {e}")
        # Show error to user
        messagebox.showerror("Error", f"Error stopping speech: {str(e)}")
        
        # Try a more aggressive cleanup
        try:
            global tts_engine
            if tts_engine:
                del tts_engine
                tts_engine = None
        except:
            pass