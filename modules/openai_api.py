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
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": transcript}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response["choices"][0]["message"]["content"]
    except openai.error.AuthenticationError:
        messagebox.showerror("Authentication Error", "Invalid API key. Please check your API key and try again.")
        openai.api_key = get_api_key()  # Prompt for API key again
        if openai.api_key:
            return generate_blog_post(transcript, prompt, model, temperature, max_tokens)  # Try again with new key
        return "Error: API key authentication failed."
    except Exception as e:
        return f"Error generating blog post: {str(e)}"