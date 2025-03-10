# Blog Post Formatter

## Description
This is a Python application that converts video transcript files into structured blog posts using OpenAI's GPT model. It reads `.txt` files containing transcripts from a selected folder or individual file, then formats the content into a well-structured blog post with a title, summary, and headings. The output is displayed in a GUI where you can easily copy or listen to the generated posts.

## New Features
- Text-to-Speech (TTS) functionality
  - Read generated blog posts aloud
  - Choose between offline and online TTS methods
  - Optimized voice selection with preferred voices
  - Voice testing with skip capability
- Process a single transcript file or an entire folder of transcripts
- Customize the formatting prompt without editing the code
- Save your API key securely between sessions
- Copy formatted blog posts to clipboard with one click
- Visual progress indicator during processing
- Multi-threaded processing to prevent UI freezing
- Modular code organization for better maintainability

## Requirements
To run this script, you need:
- Python 3.x installed on your machine
- The following Python libraries:
  - `tkinter` (for GUI, usually comes with Python)
  - `openai` (for generating blog posts via GPT)
  - `pyttsx3` (for offline text-to-speech)
  - `gtts` (for online text-to-speech)
  - `pygame` (for audio playback)

You can install the required libraries using `pip`:
```bash
pip install openai pyttsx3 gtts pygame
```

## Setup Instructions

1. **Clone or download the repository**:
   ```bash
   git clone https://github.com/yourusername/BlogPostFormatter.git
   cd BlogPostFormatter
   ```

2. **API Key**: You'll be prompted to enter your OpenAI API key when you first run the application. You can choose to save it for future use.

3. **Customizing the Prompt**: The application creates a `prompt.txt` file that contains instructions for formatting. You can edit this file using the "Edit Prompt" button.

4. **Run the Script**:
   - Navigate to the folder where `main.py` is located
   - Open a terminal or command prompt
   - Run the following command to start the application:
     ```bash
     python main.py
     ```

## Project Structure

The project is organized into modules for better maintainability:

```
BlogPostFormatter/
├── main.py                 # Main application entry point
├── config.json             # Configuration file
├── prompt.txt              # System prompt file
└── modules/
    ├── __init__.py         # Makes the directory a Python package
    ├── ui.py               # UI components and layout
    ├── settings.py         # Settings management
    ├── tts.py              # Text-to-speech functionality
    └── openai_api.py       # OpenAI API interactions
```

## How It Works

1. **API Key Management**:
   - On first run, you'll be prompted to enter your OpenAI API key
   - You can choose to save the key for future sessions
   - The "Change API Key" button allows you to update your key anytime

2. **Selecting Files**:
   - Choose between processing a single file or an entire folder
   - Click the "Select" button to browse for your transcript file(s)

3. **Text-to-Speech (TTS)**:
   - After generating a blog post, use the new TTS feature
   - Choose between two TTS methods:
     * Offline: Uses optimized system voices (pyttsx3)
     * Online: Uses Google Text-to-Speech (gTTS)
   - Click the "Speak" button to hear the generated blog post read aloud
   - Use "Test Voices" to hear samples of preferred voices
   - Adjust speech rate with the slider (faster or slower)

4. **Customizing the Format**:
   - Click "Edit Prompt" to customize how your transcripts are formatted
   - The prompt file opens in your default text editor
   - Save and close the file when you're done editing

5. **Processing**:
   - A progress bar appears during processing
   - For folders, the application shows which file is being processed

6. **Output**:
   - The formatted blog post appears in the text area
   - Click "Copy to Clipboard" to copy the entire formatted text
   - Use the "Speak" button to listen to the generated post

## Voice Optimization
The application comes pre-configured with a selection of high-quality voice options for text-to-speech, eliminating the need to search through dozens of system voices. The voice selection focuses on clear, natural-sounding options for the best user experience. Features include:

- Pre-selected high-quality voices
- "Test Voices" button to quickly hear samples
- "Skip" function to move to the next voice during testing
- Adjustable speech rate for each voice
- Voice settings saved between sessions

## Customization

You can customize how your blog posts are formatted by editing the `prompt.txt` file. The default prompt creates a structured blog post with:
- An engaging title
- A summary
- Organized headings and subheadings
- Well-structured paragraphs
- A brief conclusion

Modify this prompt to change the style, structure, or focus of your blog posts.

## Troubleshooting TTS

- **Offline TTS**: Uses optimized system voices. If you encounter issues, try testing different voices with the "Test Voices" button.
- **Online TTS**: Requires an internet connection. Provides a more natural-sounding voice but may be slower.
- If TTS doesn't work, ensure all required libraries are installed correctly.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.