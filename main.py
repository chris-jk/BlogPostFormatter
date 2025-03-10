import tkinter as tk
from modules.ui import create_ui
from modules.settings import load_settings

def main():
    # Initialize main window
    root = tk.Tk()
    root.title("Blog Post Formatter")
    root.geometry("900x700")
    
    # Create UI components
    create_ui(root)
    
    # Start the GUI event loop
    root.mainloop()

if __name__ == "__main__":
    print("""
Required Libraries:
1. pip install openai
2. pip install pyttsx3
3. pip install gtts
4. pip install pygame
5. pip install tkinter (usually comes with Python)

Note: You'll need an OpenAI API key to use this application.
""")
    main()