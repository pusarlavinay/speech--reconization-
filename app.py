import os
import queue
import threading
from datetime import datetime

import pyttsx3
import speech_recognition as sr
import streamlit as st
from streamlit_autorefresh import st_autorefresh

try:
    from streamlit.runtime.scriptrunner import get_script_run_ctx
except Exception:
    get_script_run_ctx = None


if __name__ == "__main__" and callable(get_script_run_ctx) and get_script_run_ctx() is None:
    print("This is a Streamlit app. Run it with: python -m streamlit run app.py")
    raise SystemExit(0)


def get_notes_filename():
    return f"voice_notes_{datetime.now().strftime('%Y-%m-%d')}.txt"


def save_notes_to_file(text, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)


def speak(engine, message):
    try:
        engine.say(message)
        engine.runAndWait()
    except Exception:
        pass


def speech_worker(stop_event, out_queue):
    recognizer = sr.Recognizer()
    tts_engine = pyttsx3.init()
    tts_engine.setProperty("rate", 170)

    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            out_queue.put(("status", "Listening... Speak now."))
            speak(tts_engine, "Recording started")

            while not stop_event.is_set():
                try:
                    audio = recognizer.listen(source, timeout=1, phrase_time_limit=6)
                    text = recognizer.recognize_google(audio).strip()
                    lower_text = text.lower()

                    if lower_text == "new line":
                        out_queue.put(("append", "\n"))
                        out_queue.put(("status", "Command: new line"))
                        speak(tts_engine, "New line added")
                    elif lower_text == "save":
                        out_queue.put(("save", None))
                        out_queue.put(("status", "Command: save"))
                        speak(tts_engine, "Notes saved")
                    elif lower_text == "stop":
                        out_queue.put(("stop", None))
                        out_queue.put(("status", "Command: stop"))
                        speak(tts_engine, "Stopping recording")
                        break
                    else:
                        out_queue.put(("append", text + " "))
                        out_queue.put(("status", f"Heard: {text}"))

                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    out_queue.put(("status", "Could not understand audio. Try again."))
                except sr.RequestError:
                    out_queue.put(("error", "Speech API unavailable. Check internet connection."))
                    break

    except OSError:
        out_queue.put(("error", "Microphone not found. Connect a working microphone."))
    except Exception as e:
        out_queue.put(("error", f"Unexpected error: {e}"))


st.set_page_config(page_title="Voice Notes", page_icon="🎙️", layout="centered")

st.markdown(
    """
    <style>
    .main {background-color: #f7fafc;}
    .title-box {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
    }
    .stTextArea textarea {
        border-radius: 10px;
        border: 1px solid #cbd5e1;
        font-size: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="title-box">
        <h2 style="margin:0;">Voice-Based Notes System</h2>
        <p style="margin:0.35rem 0 0 0;color:#475569;">
            Voice commands: <b>save</b>, <b>new line</b>, <b>stop</b>
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "note_text" not in st.session_state:
    st.session_state.note_text = ""
if "recording" not in st.session_state:
    st.session_state.recording = False
if "status" not in st.session_state:
    st.session_state.status = "Idle"
if "notes_file" not in st.session_state:
    st.session_state.notes_file = get_notes_filename()
if "worker_queue" not in st.session_state:
    st.session_state.worker_queue = queue.Queue()
if "stop_event" not in st.session_state:
    st.session_state.stop_event = threading.Event()
if "worker_thread" not in st.session_state:
    st.session_state.worker_thread = None


def process_worker_queue():
    q = st.session_state.worker_queue
    while not q.empty():
        action, payload = q.get()

        if action == "append":
            st.session_state.note_text += payload
        elif action == "save":
            save_notes_to_file(st.session_state.note_text, st.session_state.notes_file)
        elif action == "stop":
            st.session_state.recording = False
            st.session_state.stop_event.set()
        elif action == "status":
            st.session_state.status = payload
        elif action == "error":
            st.session_state.status = payload
            st.session_state.recording = False
            st.session_state.stop_event.set()


process_worker_queue()

if st.session_state.recording:
    st_autorefresh(interval=1000, key="voice_refresh")

c1, c2, c3 = st.columns(3)

with c1:
    if st.button("Start Recording", use_container_width=True, disabled=st.session_state.recording):
        st.session_state.stop_event = threading.Event()
        st.session_state.worker_queue = queue.Queue()

        worker = threading.Thread(
            target=speech_worker,
            args=(st.session_state.stop_event, st.session_state.worker_queue),
            daemon=True,
        )
        worker.start()
        st.session_state.worker_thread = worker
        st.session_state.recording = True
        st.session_state.status = "Starting microphone..."

with c2:
    if st.button("Stop Recording", use_container_width=True, disabled=not st.session_state.recording):
        st.session_state.stop_event.set()
        st.session_state.recording = False
        st.session_state.status = "Stopped"

with c3:
    if st.button("Save Notes", use_container_width=True):
        save_notes_to_file(st.session_state.note_text, st.session_state.notes_file)
        st.session_state.status = f"Saved to {st.session_state.notes_file}"

st.write(f"Status: {st.session_state.status}")

st.text_area("Recognized Text", value=st.session_state.note_text, height=260)

col_a, col_b = st.columns(2)
with col_a:
    if st.button("Clear Text", use_container_width=True):
        st.session_state.note_text = ""
        st.session_state.status = "Text cleared"

with col_b:
    st.download_button(
        label="Download Notes",
        data=st.session_state.note_text,
        file_name=st.session_state.notes_file,
        mime="text/plain",
        use_container_width=True,
    )

st.caption(f"Notes file path: {os.path.abspath(st.session_state.notes_file)}")
