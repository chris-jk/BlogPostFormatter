import os
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import pyttsx3
from gtts import gTTS
import pygame
import threading

from modules.settings import load_settings, save_settings, get_preferred_voices, save_preferred_voice, remove_preferred_voice

# Global variables
tts_engine = None
speech_thread = None
speech_lock = threading.Lock()  # Add a lock to prevent concurrent speech operations
is_speaking = False
stop_speaking = False
skip_voice = False
is_testing_voices = False

def initialize_engine():
    """Initialize and return a new TTS engine"""
    try:
        engine = pyttsx3.init()
        return engine
    except Exception as e:
        print(f"Error initializing TTS engine: {e}")
        return None

def stop_text_to_speech():
    """Stop current text-to-speech playback"""
    global is_speaking, stop_speaking, tts_engine, is_testing_voices, skip_voice
    
    # Set flags first to ensure they're updated even if errors occur
    stop_speaking = True
    skip_voice = True
    is_testing_voices = False
    
    try:
        # Stop any pygame playback for online TTS
        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
    except Exception as e:
        print(f"Error stopping pygame mixer: {e}")
    
    # Try to cleanly shut down the engine
    try:
        if tts_engine:
            tts_engine.stop()
    except Exception as e:
        print(f"Error stopping TTS engine: {e}")
    
    # Wait a moment to allow things to stop
    time.sleep(0.1)
    is_speaking = False
    
    # Log successful stop
    print("Speech stopped successfully")
    return True

def skip_current_voice():
    """Skip the currently speaking voice during testing"""
    global skip_voice
    skip_voice = True

def test_voices(root, output_text, button_frame):
    """Test all available voices by speaking a sample text with each voice"""
    global skip_voice, is_testing_voices, tts_engine
    
    # Prevent running if already testing
    if is_testing_voices:
        return
    
    try:
        # Reset the skip flag
        skip_voice = False
        is_testing_voices = True
        
        # Create the skip button if it doesn't exist
        if not hasattr(test_voices, 'skip_button_exists') and button_frame:
            skip_button = ttk.Button(button_frame, text="Skip Voice", command=skip_current_voice)
            skip_button.pack(side=tk.LEFT, padx=10)
            test_voices.skip_button_exists = True
        
        # Initialize a new TTS engine specifically for testing
        test_engine = initialize_engine()
        if not test_engine:
            messagebox.showerror("Error", "Failed to initialize speech engine for testing.")
            is_testing_voices = False
            return
        
        # Get available voices
        voices = test_engine.getProperty('voices')
        
        # Get preferred voice indices from settings
        preferred_indices_str = get_preferred_voices()
        preferred_indices = []
        for idx in preferred_indices_str:
            try:
                preferred_indices.append(int(idx))
            except:
                continue
        
        # Use default indices if none are set
        if not preferred_indices:
            preferred_indices = [14, 30, 38, 39, 66, 80, 89, 90, 97, 108]
        
        # Text to speak for testing
        test_text = "This is a sample of my voice. How do I sound?"
        
        # Clear the output area
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, "Testing your preferred voices...\n\n")
        output_text.see(tk.END)
        root.update_idletasks()
        
        # Only test the preferred voices that are within the range of available voices
        for i in preferred_indices:
            if i < len(voices):
                voice = voices[i]
                # Display voice information in the output text area
                output_text.insert(tk.END, f"Voice {i}: {voice.name} (ID: {voice.id})\n")
                output_text.see(tk.END)  # Scroll to see the new text
                root.update_idletasks()  # Update the UI
                
                # Set the voice
                test_engine.setProperty('voice', voice.id)
                
                # Set a moderate rate
                test_engine.setProperty('rate', 190)
                
                # Reset skip flag
                skip_voice = False
                
                # Speak the test text
                test_engine.say(f"Voice number {i}: {voice.name}. {test_text}")
                
                # Run the speech
                try:
                    test_engine.runAndWait()
                except Exception as e:
                    print(f"Error in runAndWait: {e}")
                    continue
                
                # Check if testing was stopped
                if not is_testing_voices or skip_voice:
                    break
                    
                # Brief pause between voices
                time.sleep(0.5)
        
        # Clean up
        del test_engine
        
        # Add a completion message
        output_text.insert(tk.END, "\nVoice testing completed.\n")
        output_text.see(tk.END)
        
    except Exception as e:
        messagebox.showerror("Voice Test Error", f"Error testing voices: {str(e)}")
    finally:
        is_testing_voices = False

def select_voice(root, tts_var):
    """Open a dialog to select and save the preferred voice"""
    try:
        if tts_var.get() == "offline":
            # Initialize a temporary engine for voice selection
            temp_engine = initialize_engine()
            if not temp_engine:
                messagebox.showerror("Error", "Failed to initialize speech engine.")
                return
                
            voices = temp_engine.getProperty('voices')
            voice_window = tk.Toplevel(root)
            voice_window.title("Voice Selection")
            voice_window.geometry("400x300")
            voice_window.transient(root)
            voice_window.grab_set()
            
            # Create listbox with scrollbar
            frame = ttk.Frame(voice_window, padding=10)
            frame.pack(fill=tk.BOTH, expand=True)
            
            scrollbar = ttk.Scrollbar(frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            listbox = tk.Listbox(frame)
            listbox.pack(fill=tk.BOTH, expand=True)
            
            # Configure scrollbar
            listbox.config(yscrollcommand=scrollbar.set)
            scrollbar.config(command=listbox.yview)
            
            # Get preferred voices from settings
            preferred_indices_str = get_preferred_voices()
            preferred_indices = []
            for idx in preferred_indices_str:
                try:
                    preferred_indices.append(int(idx))
                except:
                    continue
            
            # Use default indices if none are set
            if not preferred_indices:
                preferred_indices = [14, 30, 38, 39, 66, 80, 89, 90, 97, 108]
            
            # Populate list with preferred voices
            preferred_voices = []
            for i in preferred_indices:
                if i < len(voices):
                    voice = voices[i]
                    preferred_voices.append(voice)
                    listbox.insert(tk.END, f"{voice.name}")
            
            # Try to select the current voice
            settings = load_settings()
            current_voice_id = settings.get('voice_id', '')
            if current_voice_id:
                for i, voice in enumerate(preferred_voices):
                    if voice.id == current_voice_id:
                        listbox.selection_set(i)
                        listbox.see(i)
                        break
            elif preferred_voices:
                # Default to first voice if none selected
                listbox.selection_set(0)
            
            def test_voice():
                selection = listbox.curselection()
                if selection:
                    selected_voice = preferred_voices[selection[0]]
                    temp_engine.setProperty('voice', selected_voice.id)
                    temp_engine.say("This is a test of how this voice sounds.")
                    temp_engine.runAndWait()
            
            def save_voice():
                selection = listbox.curselection()
                if selection:
                    selected_voice = preferred_voices[selection[0]]
                    settings = load_settings()
                    settings['voice_id'] = selected_voice.id
                    settings['last_voice_id'] = selected_voice.id
                    success = save_settings(settings)
                    
                    # Set the voice on the global engine if it exists
                    global tts_engine
                    if tts_engine:
                        try:
                            tts_engine.setProperty('voice', selected_voice.id)
                        except:
                            # Create a new engine if setting the voice fails
                            tts_engine = initialize_engine()
                            if tts_engine:
                                tts_engine.setProperty('voice', selected_voice.id)
                    
                    voice_window.destroy()
                    if success:
                        messagebox.showinfo("Success", f"Voice set to: {selected_voice.name}")
                    else:
                        messagebox.showwarning("Warning", "Voice selection was made but settings could not be saved.")
                else:
                    messagebox.showwarning("No selection", "Please select a voice.")
            
            # Button frame
            button_frame = ttk.Frame(voice_window)
            button_frame.pack(pady=10)
            
            # Test button
            test_btn = ttk.Button(button_frame, text="Test Voice", command=test_voice)
            test_btn.pack(side=tk.LEFT, padx=5)
            
            # Save button
            save_btn = ttk.Button(button_frame, text="Save", command=save_voice)
            save_btn.pack(side=tk.LEFT, padx=5)
            
            # Cancel button
            cancel_btn = ttk.Button(button_frame, text="Cancel", command=voice_window.destroy)
            cancel_btn.pack(side=tk.LEFT, padx=5)
            
            # Clean up resources when window closes
            def on_window_close():
                del temp_engine
                voice_window.destroy()
            
            voice_window.protocol("WM_DELETE_WINDOW", on_window_close)
            
        else:
            messagebox.showinfo("Online TTS", "Voice selection is not available for online TTS.")
            
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while selecting a voice: {str(e)}")

def speak_text(root, output_text, tts_var, test_all_voices_var=None):
    """Speak the selected text with the chosen voice"""
    global tts_engine, is_speaking, stop_speaking, speech_thread
    
    # Don't start new speech if already speaking
    if is_speaking:
        return
    
    # Set flags
    is_speaking = True
    stop_speaking = False
    
    # Get the text to speak
    text = output_text.get(1.0, tk.END).strip()
    if not text:
        messagebox.showwarning("Warning", "No text to speak!")
        is_speaking = False
        return
    
    # Check if testing all voices
    if test_all_voices_var and test_all_voices_var.get():
        is_speaking = False  # Reset flag
        test_voices(root, output_text, None)
        return
    
    # Handle offline TTS
    if tts_var.get() == "offline":
        # Create speech thread
        speech_thread = threading.Thread(target=lambda: speak_offline(root, text, tts_var))
        speech_thread.daemon = True
        speech_thread.start()
    else:
        # Create speech thread for online TTS
        speech_thread = threading.Thread(target=lambda: speak_online(root, output_text, text))
        speech_thread.daemon = True
        speech_thread.start()


def speak_offline(root, text, tts_var):
    """Handle offline TTS speech in a separate thread"""
    global is_speaking, stop_speaking, tts_engine
    
    with speech_lock:  # Use lock to prevent concurrent speech
        try:
            # Create a new engine for this speech task if needed
            if not tts_engine:
                tts_engine = initialize_engine()
                
            if not tts_engine:
                messagebox.showerror("Error", "Failed to initialize speech engine.")
                is_speaking = False
                return
            
            # Get voice ID from settings
            settings = load_settings()
            voice_id = settings.get('voice_id', '')
            
            # If no voice is set but we have last_voice_id, use that instead
            if not voice_id and 'last_voice_id' in settings:
                voice_id = settings.get('last_voice_id', '')
                
                # And save it as the current voice_id for future use
                if voice_id:
                    settings['voice_id'] = voice_id
                    save_settings(settings)
            
            # If still no voice is set, prompt user to select one
            if not voice_id:
                is_speaking = False  # Reset flag so UI isn't locked
                
                # We're in a thread, so we need to use root.after to run UI code
                root.after(0, lambda: select_voice(root, tts_var))
                return
            
            # Set the voice if we have one
            if voice_id:
                try:
                    tts_engine.setProperty('voice', voice_id)
                except Exception as e:
                    print(f"Warning: Could not set voice: {e}")
                    # Try to recreate the engine
                    try:
                        del tts_engine
                        tts_engine = initialize_engine()
                        if tts_engine:
                            tts_engine.setProperty('voice', voice_id)
                    except Exception as e2:
                        print(f"Error recreating engine: {e2}")
            
            # Add a check for stop_speaking before proceeding
            if stop_speaking:
                is_speaking = False
                return
                
            # Set a moderate rate
            tts_engine.setProperty('rate', 190)
            
            # Speak the text
            tts_engine.say(text)
            
            # Update UI before runAndWait - IMPORTANT!
            root.after(0, lambda: update_speech_status(root, "Status: Speaking..."))
            
            # Run the speech - this blocks until speech is done
            tts_engine.runAndWait()
            
            # Update UI after speech is done
            root.after(0, lambda: update_speech_status(root, "Status: Speech completed"))
            
            # No need to delete the engine, we'll reuse it
            print("Speech completed successfully")
            
        except Exception as e:
            print(f"Error in speak_offline: {e}")
            root.after(0, lambda: update_speech_status(root, f"Status: Error - {str(e)[:30]}..."))
            
        finally:
            # Important: Use root.after to update flags from the main thread
            root.after(0, lambda: finish_speech())

# 2. Add this new helper function to modules/tts.py to update status safely
def update_speech_status(root, message):
    """Update speech status safely from any thread"""
    try:
        # This needs to be imported in the app.py file and set when updating status
        from modules.app_globals import speech_status
        if speech_status:
            speech_status.config(text=message)
        # Force UI update
        root.update_idletasks()
    except Exception as e:
        print(f"Error updating speech status: {e}")

# 3. Add this new helper function to modules/tts.py to reset flags safely
def finish_speech():
    """Reset speaking flags safely"""
    global is_speaking, stop_speaking
    is_speaking = False
    stop_speaking = False
    print("Speech flags reset")


def speak_online(root, output_text, text):
    """Handle online TTS using Google's service"""
    global is_speaking, stop_speaking
    
    with speech_lock:  # Use lock to prevent concurrent speech
        try:
            # Initialize pygame mixer if not already done
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            
            # Create a temp file for the speech
            temp_dir = os.path.join(os.path.dirname(__file__), "temp")
            os.makedirs(temp_dir, exist_ok=True)
            temp_file = os.path.join(temp_dir, "temp_speech.mp3")
            
            # Show progress message (in main thread)
            root.after(0, lambda: update_ui(output_text, "\n\nGenerating speech... Please wait...\n", True))
            
            # Use gTTS to generate speech
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(temp_file)
            
            # Check if user stopped while generating
            if stop_speaking:
                try:
                    os.remove(temp_file)
                except:
                    pass
                is_speaking = False
                return
            
            # Play the generated speech
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            
            # Update message (in main thread)
            root.after(0, lambda: update_ui(output_text, "Playing speech... Press Stop to end playback.\n", False))
            
            # Wait for playback to finish or user to stop
            while pygame.mixer.music.get_busy() and not stop_speaking:
                pygame.time.Clock().tick(10)  # Limit CPU usage
            
            # Clean up
            pygame.mixer.music.stop()
            try:
                os.remove(temp_file)
            except:
                pass
            
        except Exception as e:
            root.after(0, lambda: messagebox.showerror("Online TTS Error", f"Failed to generate or play speech: {str(e)}"))
            
        finally:
            is_speaking = False
            stop_speaking = False
            # Try to clean up pygame mixer
            try:
                pygame.mixer.quit()
            except:
                pass

def update_ui(output_text, message, append):
    """Update UI from background thread"""
    if append:
        output_text.insert(tk.END, message)
    else:
        output_text.delete("end-3l", tk.END)
        output_text.insert(tk.END, message)
    output_text.see(tk.END)