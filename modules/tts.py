import os
import time
import threading
import tkinter as tk
from tkinter import messagebox, ttk
import pyttsx3
from gtts import gTTS
import pygame

from modules.settings import load_settings, save_settings, get_preferred_voices, save_preferred_voice, remove_preferred_voice

# Global variables
tts_engine = None
is_speaking = False
stop_speaking = False
skip_voice = False
is_testing_voices = False

def stop_text_to_speech():
    """Stop current text-to-speech playback"""
    global is_speaking, stop_speaking, tts_engine, is_testing_voices, skip_voice
    stop_speaking = True
    skip_voice = True
    is_testing_voices = False
    if tts_engine:
        try:
            tts_engine.stop()
        except:
            pass
    is_speaking = False

def skip_current_voice():
    """Skip the currently speaking voice during testing"""
    global skip_voice
    skip_voice = True

def test_voices(root, output_text, button_frame):
    """Test all available voices by speaking a sample text with each voice"""
    global skip_voice, is_testing_voices, tts_engine
    try:
        # Reset the skip flag
        skip_voice = False
        is_testing_voices = True
        
        # Create the skip button if it doesn't exist
        if not hasattr(test_voices, 'skip_button_exists'):
            skip_button = ttk.Button(button_frame, text="Skip Voice", command=skip_current_voice)
            skip_button.pack(side=tk.LEFT, padx=10)
            test_voices.skip_button_exists = True
        
        # Initialize the TTS engine
        tts_engine = pyttsx3.init()
        
        # Get available voices
        voices = tts_engine.getProperty('voices')
        
        # Preferred voice indices - based on your selection
        preferred_indices = [14, 30, 38, 39, 66, 80, 89, 90, 97, 108]
        
        # Text to speak for testing
        test_text = "This is a sample of my voice. How do I sound?"
        
        # Clear the output area
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, "Testing your preferred voices...\n\n")
        output_text.see(tk.END)
        root.update_idletasks()
        
        # Only test the preferred voices
        for i in preferred_indices:
            if i < len(voices):
                voice = voices[i]
                # Display voice information in the output text area
                output_text.insert(tk.END, f"Voice {i}: {voice.name} (ID: {voice.id})\n")
                output_text.see(tk.END)  # Scroll to see the new text
                root.update_idletasks()  # Update the UI
                
                # Set the voice
                tts_engine.setProperty('voice', voice.id)
                
                # Set a moderate rate
                tts_engine.setProperty('rate', 190)
                
                # Reset skip flag
                skip_voice = False
                
                # Speak the test text
                tts_engine.say(f"Voice number {i}: {voice.name}. {test_text}")
                
                # Create an event for checking skip
                def check_skip():
                    if skip_voice:
                        tts_engine.stop()
                        return
                    root.after(100, check_skip)
                
                # Start checking for skip
                root.after(10, check_skip)
                
                # Run the speech
                tts_engine.runAndWait()
                
                # Check if testing was stopped
                if not is_testing_voices:
                    break
                    
                # Brief pause between voices if not skipped
                if not skip_voice:
                    time.sleep(0.5)
        
        # Add a completion message
        output_text.insert(tk.END, "\nVoice testing completed.\n")
        output_text.see(tk.END)
        
    except Exception as e:
        messagebox.showerror("Voice Test Error", f"Error testing voices: {str(e)}")
    finally:
        is_testing_voices = False

def speak_text(root, output_text, tts_var, test_all_voices_var):
    """Speak the selected text with the chosen voice"""
    global tts_engine, is_speaking, stop_speaking
    
    # Get text from output area if not provided
    text = output_text.get(1.0, tk.END).strip()
    
    if not text:
        messagebox.showwarning("Warning", "No text to speak!")
        return
    
    # Reset speaking flags
    is_speaking = False
    stop_speaking = False
    
    # Determine TTS method based on selection
    tts_method = tts_var.get()
    
    try:
        if tts_method == "offline":
            # Offline method using pyttsx3
            tts_engine = pyttsx3.init()
            
            # Get available voices
            all_voices = tts_engine.getProperty('voices')
            
            # Debug option: Test all voices
            if test_all_voices_var.get():
                test_voices(root, output_text, None)
                return
            
            # Get preferred voice IDs
            preferred_indices = [14, 30, 38, 39, 66, 80, 89, 90, 97, 108]
            
            # Get the specific voice objects
            preferred_voices = [all_voices[i] for i in preferred_indices if i < len(all_voices)]
            
            # Create a custom dialog for voice and speed selection
            voice_dialog = tk.Toplevel(root)
            voice_dialog.title("Voice and Speed Settings")
            voice_dialog.geometry("450x500")
            
            # Voice Selection
            voice_frame = ttk.LabelFrame(voice_dialog, text="Voice Selection")
            voice_frame.pack(padx=20, pady=10, fill=tk.X)
            
            # Scrollable Listbox for Voices
            voice_listbox_frame = ttk.Frame(voice_frame)
            voice_listbox_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
            
            # Scrollbar
            voice_scrollbar = ttk.Scrollbar(voice_listbox_frame)
            voice_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Listbox
            voice_listbox = tk.Listbox(voice_listbox_frame, 
                                      yscrollcommand=voice_scrollbar.set, 
                                      font=('Helvetica', 10), 
                                      selectmode=tk.SINGLE)
            voice_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            voice_scrollbar.config(command=voice_listbox.yview)
            
            # Populate voice listbox with only preferred voices
            for i, voice in enumerate(preferred_voices):
                voice_listbox.insert(tk.END, f"{voice.name}")
            
            # Speed Selection
            speed_frame = ttk.LabelFrame(voice_dialog, text="Speech Speed")
            speed_frame.pack(padx=20, pady=10, fill=tk.X)
            
            # Speed Slider
            speed_var = tk.DoubleVar(value=190)
            speed_label = ttk.Label(speed_frame, text="Speed: 190")
            speed_label.pack(pady=5)
            
            def update_speed_label(val):
                speed_val = int(float(val))
                speed_label.config(text=f"Speed: {speed_val}")
            
            speed_scale = ttk.Scale(speed_frame, 
                                   from_=50, to=300, 
                                   orient=tk.HORIZONTAL, 
                                   variable=speed_var,
                                   command=update_speed_label)
            speed_scale.pack(padx=10, pady=5, fill=tk.X)
            
            # Test selected voice
            def test_selected_voice():
                try:
                    selection = voice_listbox.curselection()
                    if selection:
                        idx = selection[0]
                        voice = preferred_voices[idx]
                        
                        # Set voice and rate
                        tts_engine.setProperty('voice', voice.id)
                        tts_engine.setProperty('rate', speed_var.get())
                        
                        # Speak test text
                        test_text = "This is a test of how this voice sounds."
                        tts_engine.say(test_text)
                        tts_engine.runAndWait()
                except Exception as e:
                    messagebox.showerror("Error", f"Could not test voice: {str(e)}")
            
            # Add test voice button
            test_button_frame = ttk.Frame(voice_dialog)
            test_button_frame.pack(pady=5)
            
            test_voice_button = ttk.Button(test_button_frame, text="Test Selected Voice", command=test_selected_voice)
            test_voice_button.pack()
            
            # Selected voice and settings
            selected_voice_idx = tk.IntVar(value=-1)
            selected_speed = tk.IntVar(value=190)
            
            # Confirm button
            def on_select():
                try:
                    # Voice selection
                    voice_selection = voice_listbox.curselection()
                    if voice_selection:
                        selected_voice_idx.set(voice_selection[0])
                    
                    # Speed selection
                    selected_speed.set(int(speed_var.get()))
                    
                    voice_dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Could not select settings: {str(e)}")
            
            # Buttons frame
            dialog_button_frame = ttk.Frame(voice_dialog)
            dialog_button_frame.pack(pady=10)
            
            confirm_button = ttk.Button(dialog_button_frame, text="Confirm", command=on_select)
            confirm_button.pack(side=tk.LEFT, padx=10)
            
            cancel_button = ttk.Button(dialog_button_frame, text="Cancel", command=voice_dialog.destroy)
            cancel_button.pack(side=tk.LEFT)
            
            # Make dialog modal
            voice_dialog.transient(root)
            voice_dialog.grab_set()
            root.wait_window(voice_dialog)
            
            # Configure TTS settings if user selected a voice
            if 0 <= selected_voice_idx.get() < len(preferred_voices):
                selected_voice = preferred_voices[selected_voice_idx.get()]
                tts_engine.setProperty('voice', selected_voice.id)
                
                # Save this as the last used voice
                settings = load_settings()
                settings['last_voice_id'] = selected_voice.id
                save_settings(settings)
            else:
                # User cancelled, so don't speak
                return
            
            # Set speaking rate
            tts_engine.setProperty('rate', selected_speed.get())
            
            # Speaking function with stop capability
            def speak_with_stop():
                global is_speaking, stop_speaking
                is_speaking = True
                try:
                    tts_engine.say(text)
                    tts_engine.runAndWait()
                except:
                    pass
                is_speaking = False
                stop_speaking = False
            
            # Start speaking in a separate thread
            speaking_thread = threading.Thread(target=speak_with_stop, daemon=True)
            speaking_thread.start()
        
        else:
            # Online method using gTTS and pygame
            tts = gTTS(text=text, lang='en')
            audio_file = "temp_speech.mp3"
            tts.save(audio_file)
            
            # Initialize pygame mixer
            pygame.mixer.init()
            
            # Load and play the audio
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            # Clean up
            pygame.mixer.music.unload()
            os.remove(audio_file)
    
    except Exception as e:
        messagebox.showerror("Text-to-Speech Error", f"Could not speak text: {str(e)}")