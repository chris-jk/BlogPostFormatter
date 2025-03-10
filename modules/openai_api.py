import os
import openai
from tkinter import messagebox, simpledialog
from modules.settings import load_settings, save_settings

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
        api_key = simpledialog.askstring("OpenAI API Key", "Enter your OpenAI API Key:", show='*')
        if not api_key:
            messagebox.showerror("Error", "API Key is required to continue.")
            return None
        
        # Ask if they want to save the key
        if messagebox.askyesno("Save API Key", "Would you like to save your API key for future use?"):
            settings = load_settings()
            settings['api_key'] = api_key
            if save_settings(settings):
                messagebox.showinfo("Success", "API key saved successfully!")
            else:
                messagebox.showwarning("Warning", "Failed to save API key.")
    
    return api_key

def set_new_api_key(api_status_label):
    """Prompt user for a new API key and save it"""
    api_key = simpledialog.askstring("OpenAI API Key", "Enter your OpenAI API Key:", show='*')
    if api_key:
        openai.api_key = api_key
        api_status_label.config(text="API Key: Set ✓")
        
        # Ask if they want to save the key
        if messagebox.askyesno("Save API Key", "Would you like to save your API key for future use?"):
            settings = load_settings()
            settings['api_key'] = api_key
            if save_settings(settings):
                messagebox.showinfo("Success", "API key saved successfully!")
            else:
                messagebox.showwarning("Warning", "Failed to save API key.")

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