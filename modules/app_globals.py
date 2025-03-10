# Status label reference that will be set by the main app
speech_status = None
is_speaking = False
stop_speaking = False

# Make sure the speech completion doesn't close the app
def update_speech_status(status_text):
    """Update the speech status text if the status label exists"""
    global speech_status
    if speech_status:
        try:
            speech_status.config(text=status_text)
        except Exception as e:
            print(f"Error updating speech status: {e}")

def set_speech_status_label(label):
    """Set the global speech_status label reference"""
    global speech_status
    speech_status = label
    print("Speech status label set successfully")