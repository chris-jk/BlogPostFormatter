# Status label reference that will be set by the main app
speech_status = None

# 5. Update your app.py to use app_globals for speech status

# At the top of app.py, add:
from modules.app_globals import speech_status as global_speech_status

# In create_ui function, after creating the speech_status label:
# Set the global reference to speech status
global_speech_status = speech_status
