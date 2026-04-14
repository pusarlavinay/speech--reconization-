# Voice-Based Notes System (Streamlit)

A beginner-friendly Speech Recognition project using Python.

## Features
- Start recording from UI button
- Speech to text using SpeechRecognition + PyAudio
- Live text shown in Streamlit
- Voice commands:
  - save
  - new line
  - stop
- Text-to-speech feedback using pyttsx3
- Save notes to file

## Project files
- app.py
- requirements.txt

## How to run (Windows CMD)

1. Open CMD
2. Go to project folder:

   cd /d D:\SpeechRecognitionNotes

3. Create virtual environment:

   python -m venv .venv

4. Activate virtual environment:

   .venv\Scripts\activate

5. Upgrade pip:

   python -m pip install --upgrade pip

6. Install dependencies:

   pip install -r requirements.txt

7. Run app:

   streamlit run app.py

8. Open browser link shown by Streamlit (usually http://localhost:8501)

## Common issues

### PyAudio installation error
- First upgrade pip and try again.
- If still failing, install matching PyAudio wheel for your Python version.

### Microphone not found
- Connect microphone.
- Set default input device in Windows sound settings.
- Restart app.

### Speech API request error
- Internet is needed for recognize_google.
- Check network and retry.

## Notes
- Saved file name format: voice_notes_YYYY-MM-DD.txt
- Use clear voice commands: save, new line, stop
