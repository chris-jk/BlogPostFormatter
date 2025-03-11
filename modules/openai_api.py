import os
import openai
import importlib.util
from tkinter import messagebox, simpledialog, ttk
import tkinter as tk
import webbrowser
from modules.settings import load_settings, save_settings, OPENAI_API_KEY_URL
from modules.rtf_converter import markdown_to_docx, save_as_docx, markdown_to_rtf

# Check if the new OpenAI client is available (v1.0.0+)
has_new_openai_client = False
openai_client = None
try:
    from openai import OpenAI
    has_new_openai_client = True
except ImportError:
    print("Warning: Using legacy OpenAI package. Some features may not work correctly.")
    has_new_openai_client = False

# Flag to track if we're using OpenRouter
using_openrouter = False

# Load the OpenRouter setting from settings
settings = load_settings()
if settings.get('use_openrouter', False):
    using_openrouter = True

def detect_key_type(api_key):
    """Detect if the API key is from OpenRouter or OpenAI"""
    # OpenRouter keys typically start with sk-or-v1
    if api_key and api_key.startswith("sk-or-"):
        return "openrouter"
    # OpenAI keys typically start with sk-
    elif api_key and api_key.startswith("sk-"):
        return "openai"
    else:
        return "unknown"

def get_api_key():
    """Get API key from environment, config file, or prompt user"""
    global openai_client, using_openrouter
    
    # First try from environment
    api_key = os.environ.get("OPENAI_API_KEY")
    
    # If not in environment, try from config file
    if not api_key:
        settings = load_settings()
        api_key = settings.get('api_key', '')
        
        # If there's a setting for OpenRouter, respect it
        if 'use_openrouter' in settings:
            using_openrouter = settings.get('use_openrouter')
    
    # If still not found, prompt user
    if not api_key:
        # Use the enhanced dialog that includes the "Get API Key" button
        show_api_key_popup()
        
        # After the popup is closed, check if API key is set
        settings = load_settings()
        api_key = settings.get('api_key', '')
        
        if not api_key:
            messagebox.showerror("Error", "API Key is required to continue.")
            return None
    
    # Detect key type
    key_type = detect_key_type(api_key)
    if key_type == "openrouter":
        # Force OpenRouter mode if the key is from OpenRouter
        using_openrouter = True
        settings = load_settings()
        settings['use_openrouter'] = True
        save_settings(settings)
        print("Debug: OpenRouter key detected, setting using_openrouter=True")
    
    # Initialize the appropriate client based on key type and available package
    if using_openrouter:
        if has_new_openai_client:
            try:
                # For OpenRouter, we use the new client with the OpenRouter base URL
                openai_client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=api_key
                )
                print("Debug: Initialized OpenRouter client")
            except Exception as e:
                print(f"Error initializing OpenRouter client: {str(e)}")
                messagebox.showerror("Error", f"Failed to initialize OpenRouter client: {str(e)}")
        else:
            # Show warning if trying to use OpenRouter without the right package
            error_msg = "Error: OpenRouter integration requires OpenAI Python package v1.0.0+.\nPlease upgrade with: pip install --upgrade openai"
            if key_type == "openrouter":
                messagebox.showerror("Package Upgrade Required", error_msg)
            print(error_msg)
    else:
        # For standard OpenAI, use the legacy API
        openai.api_key = api_key
        print("Debug: Set legacy OpenAI API key")
    
    return api_key

def set_new_api_key(api_status_label):
    """Prompt user for a new API key using the enhanced popup"""
    global openai_client, using_openrouter
    
    show_api_key_popup()
    
    # Update the status label
    settings = load_settings()
    api_key = settings.get('api_key', '')
    
    if api_key:
        # Detect key type
        key_type = detect_key_type(api_key)
        
        if key_type == "openrouter":
            # Force OpenRouter mode if key is from OpenRouter
            using_openrouter = True
            settings['use_openrouter'] = True
            save_settings(settings)
            
            if has_new_openai_client:
                try:
                    openai_client = OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=api_key
                    )
                    api_status_label.config(text="API Key: Set (OpenRouter) ✓")
                    print("Debug: Initialized OpenRouter client in set_new_api_key")
                    return
                except Exception as e:
                    print(f"Error initializing OpenRouter client: {str(e)}")
                    messagebox.showerror("Error", f"Failed to initialize OpenRouter client: {str(e)}")
                    api_status_label.config(text="API Key: Error with OpenRouter!")
                    return
            else:
                error_msg = "Error: OpenRouter integration requires OpenAI Python package v1.0.0+.\nPlease upgrade with: pip install --upgrade openai"
                messagebox.showerror("Package Upgrade Required", error_msg)
                api_status_label.config(text="API Key: Error (Upgrade Required)")
                return
        else:
            # Standard OpenAI key
            openai.api_key = api_key
            api_status_label.config(text="API Key: Set (OpenAI) ✓")
            print("Debug: Set standard OpenAI key in set_new_api_key")

def open_api_key_website():
    """Open the API key website in the default browser"""
    global using_openrouter
    
    # If we're using OpenRouter, redirect to OpenRouter instead
    url = "https://openrouter.ai/keys" if using_openrouter else OPENAI_API_KEY_URL
    
    try:
        webbrowser.open(url)
        return True
    except Exception as e:
        error_msg = f"Error opening API key website: {str(e)}"
        print(error_msg)
        messagebox.showerror("Error", error_msg)
        # Last resort - show the URL to the user
        messagebox.showinfo("API Key URL", f"Please visit: {url}")
        return False

def show_api_key_popup():
    """Show a popup window for API key management with a button to get an API key"""
    global using_openrouter
    
    # Create a popup window
    popup = tk.Toplevel()
    
    # Set title based on whether we're using OpenRouter
    api_service = "OpenRouter" if using_openrouter else "OpenAI"
    popup.title(f"{api_service} API Key Settings")
    
    popup.geometry("500x240")
    popup.transient(tk._default_root)
    popup.grab_set()
    
    # Create and place widgets
    ttk.Label(popup, text=f"Enter your {api_service} API Key:").pack(pady=(10, 0))
    
    # Load current key
    settings = load_settings()
    api_key_var = tk.StringVar(value=settings.get('api_key', ''))
    api_key_entry = ttk.Entry(popup, width=40, textvariable=api_key_var)
    api_key_entry.pack(pady=(10, 0))
    
    # Detect key type if one exists
    if api_key_var.get():
        key_type = detect_key_type(api_key_var.get())
        key_info = ttk.Label(
            popup, 
            text=f"Detected key type: {key_type.upper()}", 
            foreground="blue" if key_type == "openrouter" else "black"
        )
        key_info.pack(pady=(5, 0))
    
    # Check if OpenRouter can be used based on OpenAI package version
    openrouter_available = has_new_openai_client
    
    # Add OpenRouter toggle
    openrouter_var = tk.BooleanVar(value=using_openrouter)
    
    def toggle_openrouter():
        global using_openrouter
        using_openrouter = openrouter_var.get() and openrouter_available
        api_service = "OpenRouter" if using_openrouter else "OpenAI"
        get_key_label.config(text=f"Don't have an {api_service} API key?")
        popup.title(f"{api_service} API Key Settings")
        
        # Update key detection if key exists
        if api_key_var.get():
            key_type = detect_key_type(api_key_var.get())
            if key_type == "openrouter" and not using_openrouter:
                warning_text = "Warning: This appears to be an OpenRouter key.\nEnable 'Use OpenRouter' for proper functionality."
                messagebox.showwarning("Key Type Mismatch", warning_text)
            elif key_type == "openai" and using_openrouter:
                warning_text = "Warning: This appears to be an OpenAI key.\nDisable 'Use OpenRouter' for proper functionality."
                messagebox.showwarning("Key Type Mismatch", warning_text)
    
    # Show warning if OpenRouter not available due to package version
    if not openrouter_available:
        warning_text = "Warning: OpenRouter support requires OpenAI package v1.0.0+\nRun: pip install --upgrade openai"
        warning_label = ttk.Label(popup, text=warning_text, foreground="red")
        warning_label.pack(pady=(5, 0))
    
    # Add checkbox (enabled only if package version supports it)
    openrouter_check = ttk.Checkbutton(
        popup, 
        text="Use OpenRouter (for DeepSeek models)", 
        variable=openrouter_var,
        command=toggle_openrouter,
        state="normal" if openrouter_available else "disabled"
    )
    openrouter_check.pack(pady=(5, 0))
    
    # Don't have an API key label
    get_key_label = ttk.Label(popup, text=f"Don't have an {api_service} API key?")
    get_key_label.pack(pady=(10, 0))
    
    # Button frame
    btn_frame = ttk.Frame(popup)
    btn_frame.pack(pady=(5, 0))
    
    def save_and_close():
        api_key = api_key_var.get().strip()
        if api_key:
            settings = load_settings()
            settings['api_key'] = api_key
            
            # Auto-detect key type if it's clear
            key_type = detect_key_type(api_key)
            if key_type == "openrouter":
                using_openrouter = True
                settings['use_openrouter'] = True
            elif key_type == "openai" and not openrouter_var.get():
                using_openrouter = False
                settings['use_openrouter'] = False
            else:
                # Otherwise use the toggle value (if available)
                if openrouter_available:
                    using_openrouter = openrouter_var.get()
                    settings['use_openrouter'] = openrouter_var.get()
            
            if save_settings(settings):
                # Initialize the right client based on settings
                if using_openrouter:
                    if has_new_openai_client:
                        try:
                            global openai_client
                            openai_client = OpenAI(
                                base_url="https://openrouter.ai/api/v1",
                                api_key=api_key
                            )
                            print("Debug: Initialized OpenRouter client in save_and_close")
                        except Exception as e:
                            print(f"Error initializing OpenRouter client: {str(e)}")
                    else:
                        print("Warning: OpenRouter selected but not available due to package version")
                else:
                    # For standard OpenAI
                    openai.api_key = api_key
                    print("Debug: Set standard OpenAI key in save_and_close")
                
                messagebox.showinfo("Success", "API key saved successfully!")
                popup.destroy()
            else:
                messagebox.showerror("Error", "Failed to save API key")
        else:
            messagebox.showwarning("Warning", "Please enter an API key")
    
    # Add a button to get an API key - this is the main focus
    get_key_btn = ttk.Button(btn_frame, text="Get API Key", command=open_api_key_website)
    get_key_btn.pack(side=tk.LEFT, padx=(0, 10))
    
    # Save button
    save_btn = ttk.Button(btn_frame, text="Save", command=save_and_close)
    save_btn.pack(side=tk.LEFT)
    
    # Add a button to upgrade OpenAI package if needed
    if not openrouter_available:
        upgrade_frame = ttk.Frame(popup)
        upgrade_frame.pack(pady=(10, 0))
        
        def show_upgrade_instructions():
            instructions = """To upgrade the OpenAI package and enable OpenRouter support:

1. Open a terminal/command prompt
2. Run: pip install --upgrade openai
3. Restart this application

This will install the latest version of the OpenAI Python package which is required for DeepSeek models."""
            messagebox.showinfo("Upgrade Instructions", instructions)
        
        upgrade_btn = ttk.Button(
            upgrade_frame, 
            text="How to Upgrade OpenAI Package", 
            command=show_upgrade_instructions
        )
        upgrade_btn.pack()
    
    # Center the popup
    popup.update_idletasks()
    width = popup.winfo_width()
    height = popup.winfo_height()
    x = (popup.winfo_screenwidth() // 2) - (width // 2)
    y = (popup.winfo_screenheight() // 2) - (height // 2)
    popup.geometry(f"{width}x{height}+{x}+{y}")

def generate_blog_post(transcript, prompt, model, temperature, max_tokens):
    """Generate a blog post from a transcript using the OpenAI API or OpenRouter"""
    global openai_client, using_openrouter
    
    try:
        print("Debug: Starting generate_blog_post")
        print(f"Debug: Transcript type: {type(transcript)}")
        print(f"Debug: Transcript has name attribute: {hasattr(transcript, 'name')}")
        print(f"Debug: Using model: {model}")
        
        # Determine if we should use OpenRouter based on model or global flag
        is_deepseek = "deepseek" in model
        needs_openrouter = is_deepseek or using_openrouter
        
        # Determine endpoint and print debug info
        if needs_openrouter:
            print(f"Debug: Using OpenRouter API (using_openrouter={using_openrouter}, is_deepseek={is_deepseek})")
        else:
            print(f"Debug: Using OpenAI API")
        
        # Fail fast if no filename
        if not hasattr(transcript, 'name'):
            error_msg = "Error: No filename provided for the transcript"
            print(f"Debug: {error_msg}")
            return error_msg

        # Get base filename from transcript name
        base_name = os.path.splitext(os.path.basename(transcript.name))[0]
        print(f"Debug: Using filename: {base_name}")
        
        # Check if we can use OpenRouter at all for models that need it
        if needs_openrouter and not has_new_openai_client:
            error_msg = "Error: DeepSeek models require OpenAI package v1.0.0+. Please upgrade with: pip install --upgrade openai"
            print(f"Debug: {error_msg}")
            return error_msg
        
        # Get the API key and make sure it's the right type
        settings = load_settings()
        api_key = settings.get('api_key', '')
        key_type = detect_key_type(api_key)
        
        if needs_openrouter and key_type == "openai":
            error_msg = "Error: You're trying to use OpenRouter with an OpenAI API key. Please use an OpenRouter API key instead."
            print(f"Debug: {error_msg}")
            return error_msg
        
        if not needs_openrouter and key_type == "openrouter":
            error_msg = "Error: You're trying to use OpenAI with an OpenRouter API key. Please use an OpenAI API key instead."
            print(f"Debug: {error_msg}")
            return error_msg
        
        # Initialize the OpenRouter client if needed but not already done
        if needs_openrouter and has_new_openai_client and openai_client is None:
            try:
                openai_client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=api_key
                )
                print("Debug: Initialized OpenRouter client in generate_blog_post")
            except Exception as e:
                error_msg = f"Error initializing OpenRouter client: {str(e)}"
                print(f"Debug: {error_msg}")
                return error_msg

        # Prepare system prompt
        system_prompt = prompt + "\nFormat your response using Markdown syntax."
        
        # Get API response based on client type
        print("Debug: Attempting API call...")
        
        if needs_openrouter and has_new_openai_client:
            # Use new client API with OpenRouter
            try:
                response = openai_client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": str(transcript)}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    extra_headers={
                        "HTTP-Referer": "AI Blog Post Generator",
                        "X-Title": "AI Blog Post Generator"
                    }
                )
                markdown_text = response.choices[0].message.content
            except Exception as e:
                error_msg = f"Error with OpenRouter API: {str(e)}"
                print(f"Debug: {error_msg}")
                return error_msg
        else:
            # Use legacy OpenAI API
            try:
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": str(transcript)}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                markdown_text = response["choices"][0]["message"]["content"]
            except Exception as e:
                error_msg = f"Error with OpenAI API: {str(e)}"
                print(f"Debug: {error_msg}")
                return error_msg
                
        print("Debug: API call successful, received response")
        
        # Convert markdown to RTF
        rtf_content = markdown_to_rtf(markdown_text)
        
        # Create output directory
        os.makedirs("blog_posts", exist_ok=True)
        
        # Generate filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"blog_posts/{base_name}_{timestamp}.rtf"
        
        # Save as RTF
        with open(filename, "w", encoding="utf-8") as f:
            f.write(rtf_content)
        print(f"Debug: Successfully saved to: {filename}")
        
        return markdown_text  # Return markdown for display in UI
            
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(f"Debug: {error_msg}")
        return error_msg

def process_multiple_files(files, prompt, model, temperature, max_tokens):
    """Process multiple files and generate blog posts for each"""
    results = []
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create named string with file path
            class NamedString(str): pass
            named_content = NamedString(content)
            named_content.name = file_path
            
            # Generate blog post
            result = generate_blog_post(named_content, prompt, model, temperature, max_tokens)
            
            # Check result type (string = success)
            if isinstance(result, str) and not result.startswith("Error:"):
                results.append((file_path, result))
                print(f"Successfully processed: {file_path}")
            else:
                print(f"Failed to process {file_path}: {result}")
                
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
            continue
    
    return results