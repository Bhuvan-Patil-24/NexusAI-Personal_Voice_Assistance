import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import speech_recognition as sr
import av
from datetime import datetime
import numpy as np

# Set up recognizer class
class AudioProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.audio_buffer = b""

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        audio = frame.to_ndarray().flatten().astype(np.int16).tobytes()
        self.audio_buffer += audio
        return frame

    def get_text(self):
        if not self.audio_buffer:
            return None
        try:
            audio_data = sr.AudioData(self.audio_buffer, 16000, 2)
            return self.recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand."
        except sr.RequestError:
            return "Speech Recognition API error."


# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []
if "voice_text" not in st.session_state:
    st.session_state.voice_text = ""

# Page styling
st.markdown("""
    <style>
    .mic-button {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background: linear-gradient(45deg, #7b2ff7, #f107a3);
        box-shadow: 0 0 10px #f107a3, 0 0 20px #7b2ff7;
        animation: pulse 1.5s infinite;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
        margin-top: 20px;
    }

    .mic-icon {
        font-size: 40px;
        color: white;
    }

    @keyframes pulse {
        0% {
            box-shadow: 0 0 0 0 rgba(241, 7, 163, 0.7);
        }
        70% {
            box-shadow: 0 0 0 20px rgba(241, 7, 163, 0);
        }
        100% {
            box-shadow: 0 0 0 0 rgba(241, 7, 163, 0);
        }
    }

    .sidebar-title {
        font-size: 20px;
        font-weight: bold;
        color: #6c63ff;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar for history
st.sidebar.markdown('<div class="sidebar-title">🕓 Message History</div>', unsafe_allow_html=True)
for msg in st.session_state.history:
    st.sidebar.markdown(f"**{msg['role']}**: {msg['message']}  \n`{msg['time']}`")

# Main title
st.title("🤖 Nexus - Your Voice Assistant")
st.subheader("🎙️ Speak to Nexus")

# Initialize processor
processor = AudioProcessor()

# Start webrtc stream
audio_ctx = webrtc_streamer(
    key="nexus",
    mode=WebRtcMode.RECVONLY,
    audio_frame_callback=processor.recv,
    media_stream_constraints={"audio": True, "video": False}
)

# Button to stop & transcribe
if audio_ctx and audio_ctx.state.playing:
    st.success("🎧 Listening... click the button below to transcribe.")
    if st.button("🔴 Stop & Transcribe"):
        user_input = processor.get_text()
        st.session_state.voice_text = user_input

# Combine with text input
typed_input = st.chat_input("Type here or speak...")
final_input = typed_input or st.session_state.voice_text

# Process input
if final_input:
    timestamp = datetime.now().strftime("%H:%M")
    st.session_state.history.append({"role": "User", "message": final_input, "time": timestamp})
    with st.chat_message("user"):
        st.markdown(final_input)
        st.caption(timestamp)

    response = f"Nexus heard: **{final_input}**. How can I assist you?"
    reply_time = datetime.now().strftime("%H:%M")
    st.session_state.history.append({"role": "Nexus", "message": response, "time": reply_time})
    with st.chat_message("assistant"):
        st.markdown(response)
        st.caption(reply_time)

    st.session_state.voice_text = ""

# Glowing mic animation
st.markdown("""
    <div class="mic-button">
        <span class="mic-icon">🎤</span>
    </div>
""", unsafe_allow_html=True)
