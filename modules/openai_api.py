import os
import openai
from tkinter import messagebox, simpledialog, ttk
import tkinter as tk
import webbrowser  # Directly import webbrowser for reliability
from modules.settings import load_settings, save_settings, OPENAI_API_KEY_URL

def get_api_key():
    """Get API key from environment, config file, or prompt user"""
    # First try from environment
    api_key = os.environ.get("OPENAI_API_KEY")
    
    # If not in environment, try from config file
    if not api_key:
        settings = load_settings()
        api_key = settings.get('api_key', '')
    
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
    
    return api_key

def set_new_api_key(api_status_label):
    """Prompt user for a new API key using the enhanced popup"""
    show_api_key_popup()
    
    # Update the status label
    settings = load_settings()
    api_key = settings.get('api_key', '')
    if api_key:
        openai.api_key = api_key
        api_status_label.config(text="API Key: Set ✓")

def open_api_key_website():
    """Open the OpenAI API key website in the default browser"""
    try:
        webbrowser.open(OPENAI_API_KEY_URL)
        return True
    except Exception as e:
        error_msg = f"Error opening API key website: {str(e)}"
        print(error_msg)
        messagebox.showerror("Error", error_msg)
        # Last resort - show the URL to the user
        messagebox.showinfo("API Key URL", f"Please visit: {OPENAI_API_KEY_URL}")
        return False

def show_api_key_popup():
    """Show a popup window for API key management with a button to get an API key"""
    # Create a popup window
    popup = tk.Toplevel()
    popup.title("API Key Settings")
    popup.geometry("400x150")
    popup.transient(tk._default_root)
    popup.grab_set()
    
    # Create and place widgets
    ttk.Label(popup, text="Enter your OpenAI API Key:").pack(pady=(10, 0))
    
    api_key_var = tk.StringVar(value=load_settings().get('api_key', ''))
    api_key_entry = ttk.Entry(popup, width=40, textvariable=api_key_var)
    api_key_entry.pack(pady=(10, 0))
    
    # Don't have an API key label
    ttk.Label(popup, text="Don't have an API key?").pack(pady=(10, 0))
    
    # Button frame
    btn_frame = ttk.Frame(popup)
    btn_frame.pack(pady=(5, 0))
    
    def save_and_close():
        api_key = api_key_var.get().strip()
        if api_key:
            settings = load_settings()
            settings['api_key'] = api_key
            openai.api_key = api_key
            if save_settings(settings):
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
    
    # Center the popup
    popup.update_idletasks()
    width = popup.winfo_width()
    height = popup.winfo_height()
    x = (popup.winfo_screenwidth() // 2) - (width // 2)
    y = (popup.winfo_screenheight() // 2) - (height // 2)
    popup.geometry(f"{width}x{height}+{x}+{y}")

def generate_blog_post(transcript, prompt, model, temperature, max_tokens):
    """Generate a blog post from a transcript using the OpenAI API"""
    try:
        print("Debug: Starting generate_blog_post")
        print(f"Debug: Transcript type: {type(transcript)}")
        print(f"Debug: Transcript has name attribute: {hasattr(transcript, 'name')}")
        
        # Fail fast if no filename
        if not hasattr(transcript, 'name'):
            error_msg = "Error: No filename provided for the transcript"
            print(f"Debug: {error_msg}")
            return error_msg

        # Get base filename from transcript name
        base_name = os.path.splitext(os.path.basename(transcript.name))[0]
        print(f"Debug: Using filename: {base_name}")

        # Get API response
        print("Debug: Attempting API call...")
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": str(transcript)}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        print("Debug: API call successful, received response")
        generated_text = response["choices"][0]["message"]["content"]
        
        # Create output directory
        os.makedirs("blog_posts", exist_ok=True)
        
        # Generate filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"blog_posts/{base_name}_{timestamp}.txt"
        
        # Save the generated text
        with open(filename, "w", encoding="utf-8") as f:
            f.write(generated_text)
        print(f"Debug: Successfully saved to: {filename}")
        return generated_text
            
    except openai.error.AuthenticationError:
        error_msg = "Authentication error with OpenAI API"
        print(f"Debug: {error_msg}")
        return error_msg
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