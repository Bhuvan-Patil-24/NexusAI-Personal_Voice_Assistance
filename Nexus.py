import streamlit as st
import speech_recognition as sr
import numpy as np
from datetime import datetime
import io
import wave

# Only import webrtc components if we're in a proper Streamlit session
try:
    from streamlit_webrtc import webrtc_streamer, WebRtcMode
    import av
    WEBRTC_AVAILABLE = True
except ImportError:
    WEBRTC_AVAILABLE = False

# Check if we're running in a proper Streamlit context
def is_streamlit_running():
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx() is not None
    except:
        return False

# Audio processor class
class AudioProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.audio_buffer = b""
        self.sample_rate = 16000

    def recv(self, frame):
        if hasattr(frame, 'to_ndarray'):
            audio = frame.to_ndarray().flatten().astype(np.int16).tobytes()
            self.audio_buffer += audio
        return frame

    def get_text(self):
        if not self.audio_buffer:
            return None
        try:
            audio_data = sr.AudioData(self.audio_buffer, self.sample_rate, 2)
            return self.recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand that."
        except sr.RequestError as e:
            return f"Speech Recognition API error: {e}"
        except Exception as e:
            return f"Error processing audio: {e}"

    def clear_buffer(self):
        self.audio_buffer = b""

# Alternative audio recording using browser's native capabilities
def create_audio_recorder():
    st.markdown("""
    <div id="audioRecorder">
        <button id="startBtn" onclick="startRecording()">🎤 Start Recording</button>
        <button id="stopBtn" onclick="stopRecording()" disabled>⏹️ Stop Recording</button>
        <div id="status"></div>
    </div>
    
    <script>
    let mediaRecorder;
    let audioChunks = [];
    
    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            
            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };
            
            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const reader = new FileReader();
                reader.onload = () => {
                    // Here you would send the audio data to Streamlit
                    console.log('Audio recorded');
                };
                reader.readAsDataURL(audioBlob);
                audioChunks = [];
            };
            
            mediaRecorder.start();
            document.getElementById('startBtn').disabled = true;
            document.getElementById('stopBtn').disabled = false;
            document.getElementById('status').innerHTML = '🔴 Recording...';
        } catch (err) {
            console.error('Error accessing microphone:', err);
            document.getElementById('status').innerHTML = '❌ Error accessing microphone';
        }
    }
    
    function stopRecording() {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
            document.getElementById('status').innerHTML = '✅ Recording stopped';
        }
    }
    </script>
    """, unsafe_allow_html=True)

# Main app function
def main():
    # Page configuration
    st.set_page_config(
        page_title="Nexus Voice Assistant",
        page_icon="🤖",
        layout="wide"
    )

    # Initialize session state
    if "history" not in st.session_state:
        st.session_state.history = []
    if "voice_text" not in st.session_state:
        st.session_state.voice_text = ""
    if "processor" not in st.session_state:
        st.session_state.processor = AudioProcessor()

    # Custom CSS
    st.markdown("""
        <style>
        .main-header {
            text-align: center;
            color: #6c63ff;
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        
        .sub-header {
            text-align: center;
            color: #8b5cf6;
            font-size: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .mic-container {
            display: flex;
            justify-content: center;
            margin: 2rem 0;
        }
        
        .mic-button {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            background: linear-gradient(45deg, #7b2ff7, #f107a3);
            box-shadow: 0 0 20px rgba(241, 7, 163, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            animation: pulse 2s infinite;
            cursor: pointer;
        }
        
        .mic-button:hover {
            transform: scale(1.1);
            transition: transform 0.2s;
        }
        
        .mic-icon {
            font-size: 50px;
            color: white;
        }
        
        @keyframes pulse {
            0% {
                box-shadow: 0 0 0 0 rgba(241, 7, 163, 0.7);
            }
            70% {
                box-shadow: 0 0 0 30px rgba(241, 7, 163, 0);
            }
            100% {
                box-shadow: 0 0 0 0 rgba(241, 7, 163, 0);
            }
        }
        
        .chat-message {
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .user-message {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-left: 20%;
        }
        
        .assistant-message {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            margin-right: 20%;
        }
        
        .sidebar-title {
            font-size: 1.2rem;
            font-weight: bold;
            color: #6c63ff;
            margin-bottom: 1rem;
        }
        
        .error-message {
            background-color: #fee;
            color: #c33;
            padding: 1rem;
            border-radius: 5px;
            border-left: 4px solid #c33;
        }
        
        .success-message {
            background-color: #efe;
            color: #3c3;
            padding: 1rem;
            border-radius: 5px;
            border-left: 4px solid #3c3;
        }
        </style>
    """, unsafe_allow_html=True)

    # Sidebar for history
    with st.sidebar:
        st.markdown('<div class="sidebar-title">🕓 Conversation History</div>', unsafe_allow_html=True)
        
        if st.button("🗑️ Clear History"):
            st.session_state.history = []
            st.rerun()
        
        for i, msg in enumerate(reversed(st.session_state.history[-10:])):  # Show last 10 messages
            with st.container():
                st.markdown(f"**{msg['role']}** ({msg['time']})")
                st.markdown(f"_{msg['message'][:50]}{'...' if len(msg['message']) > 50 else ''}_")
                st.divider()

    # Main content
    st.markdown('<h1 class="main-header">🤖 Nexus AI Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">🎙️ Your Intelligent Voice Companion</p>', unsafe_allow_html=True)

    # Check if we're in a proper Streamlit session
    if not is_streamlit_running():
        st.markdown("""
        <div class="error-message">
            <h3>⚠️ Incorrect Launch Method</h3>
            <p>Please run this app using the command:</p>
            <code>streamlit run Nexus.py</code>
            <p>Do not use <code>python -u</code> to run Streamlit applications.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # Voice input section
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if WEBRTC_AVAILABLE:
            try:
                # WebRTC Audio Streaming
                st.markdown("### 🎤 Voice Input")
                
                audio_ctx = webrtc_streamer(
                    key="nexus-audio",
                    mode=WebRtcMode.RECVONLY,
                    audio_frame_callback=st.session_state.processor.recv,
                    media_stream_constraints={"audio": True, "video": False},
                    async_processing=True,
                )
                
                if audio_ctx.state.playing:
                    st.markdown('<div class="success-message">🎧 Listening... Click "Stop & Process" when done speaking.</div>', unsafe_allow_html=True)
                    
                    if st.button("🔴 Stop & Process Audio", key="stop_audio"):
                        transcribed_text = st.session_state.processor.get_text()
                        if transcribed_text:
                            st.session_state.voice_text = transcribed_text
                            st.session_state.processor.clear_buffer()
                            st.rerun()
                
                # Glowing microphone animation
                st.markdown("""
                    <div class="mic-container">
                        <div class="mic-button">
                            <span class="mic-icon">🎤</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"WebRTC Error: {e}")
                st.info("WebRTC microphone access failed. Please use the text input below.")
        else:
            st.warning("WebRTC components not available. Using text input only.")

    # Text input
    st.markdown("### 💬 Text Input")
    typed_input = st.chat_input("Type your message here or use voice input above...")
    
    # Process input (voice or text)
    final_input = typed_input or st.session_state.voice_text
    
    if final_input:
        # Clear voice text after processing
        if st.session_state.voice_text:
            st.session_state.voice_text = ""
        
        # Add user message to history
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.history.append({
            "role": "User", 
            "message": final_input, 
            "time": timestamp
        })
        
        # Generate response (you can integrate with actual AI here)
        response = generate_response(final_input)
        reply_time = datetime.now().strftime("%H:%M:%S")
        
        st.session_state.history.append({
            "role": "Nexus", 
            "message": response, 
            "time": reply_time
        })
        
        st.rerun()

    # Display conversation
    st.markdown("### 💭 Conversation")
    for msg in st.session_state.history[-5:]:  # Show last 5 messages
        if msg["role"] == "User":
            st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>👤 You</strong> <small>({msg['time']})</small><br>
                    {msg['message']}
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>🤖 Nexus</strong> <small>({msg['time']})</small><br>
                    {msg['message']}
                </div>
            """, unsafe_allow_html=True)

def generate_response(user_input):
    """Generate a response to user input (placeholder for actual AI integration)"""
    user_input_lower = user_input.lower()
    
    if "hello" in user_input_lower or "hi" in user_input_lower:
        return "Hello! I'm Nexus, your AI assistant. How can I help you today?"
    elif "how are you" in user_input_lower:
        return "I'm doing great, thank you for asking! I'm here and ready to assist you."
    elif "time" in user_input_lower:
        return f"The current time is {datetime.now().strftime('%H:%M:%S')}."
    elif "date" in user_input_lower:
        return f"Today's date is {datetime.now().strftime('%B %d, %Y')}."
    elif "weather" in user_input_lower:
        return "I don't have access to real-time weather data, but I'd be happy to help you find a weather service!"
    elif "bye" in user_input_lower or "goodbye" in user_input_lower:
        return "Goodbye! It was nice talking with you. Have a great day!"
    else:
        return f"I heard you say: '{user_input}'. I'm still learning, but I'm here to help! What would you like to know?"

if __name__ == "__main__":
    main()