import streamlit as st
import speech_recognition as sr
import numpy as np
from datetime import datetime
import time

# Only import webrtc components if available
try:
    from streamlit_webrtc import webrtc_streamer, WebRtcMode
    WEBRTC_AVAILABLE = True
except ImportError:
    WEBRTC_AVAILABLE = False

# Import your NexusAI backend components
try:
    from config import WAKE_WORD
    from nlp_processor import NLPProcessor
    from data_manager import DataManager
    from audio_handler import AudioHandler
    from command_processor import CommandProcessor
    NEXUS_BACKEND_AVAILABLE = True
except ImportError as e:
    NEXUS_BACKEND_AVAILABLE = False
    IMPORT_ERROR = str(e)

# Check if we're running in a proper Streamlit context
def is_streamlit_running():
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx() is not None
    except:
        return False

# Streamlit-compatible NexusAI wrapper
class StreamlitNexusAI:
    def __init__(self):
        if not NEXUS_BACKEND_AVAILABLE:
            raise ImportError(f"NexusAI backend components not available: {IMPORT_ERROR}")
        
        # Initialize core components (same as original NexusAI)
        self.data_manager = DataManager()
        self.nlp_processor = NLPProcessor()
        self.audio_handler = AudioHandler()
        self.command_processor = CommandProcessor(
            self.nlp_processor, 
            self.data_manager
        )
        
        # Assistant state
        self.is_listening = False
        self.wake_word = WAKE_WORD.lower()
        self.running = True
        
        # Streamlit-specific state
        self.last_response = ""
        self.conversation_history = []
        
    def process_input(self, user_input):
        """Process user input and return response"""
        try:
            # Check for wake word or if already listening
            if self.wake_word in user_input.lower() or self.is_listening:
                # Process the command using your existing command processor
                response, should_exit = self.command_processor.process_command(user_input)
                
                # Add to conversation history
                self.conversation_history.append({
                    "role": "User",
                    "message": user_input,
                    "time": datetime.now().strftime("%H:%M:%S")
                })
                
                self.conversation_history.append({
                    "role": "Nexus",
                    "message": response,
                    "time": datetime.now().strftime("%H:%M:%S")
                })
                
                # Set listening state for follow-up commands
                self.is_listening = True
                
                # Schedule reset of listening state (simulated)
                # In Streamlit, we'll handle this differently
                
                return response, should_exit
            else:
                return f"Please say '{WAKE_WORD}' followed by your command to activate me.", False
                
        except Exception as e:
            error_msg = f"Error processing command: {str(e)}"
            return error_msg, False
    
    def get_system_info(self):
        """Get system information"""
        info = {
            'is_listening': self.is_listening,
            'wake_word': self.wake_word,
            'running': self.running,
            'conversation_count': len(self.conversation_history),
            'data_info': self.data_manager.get_storage_info() if hasattr(self.data_manager, 'get_storage_info') else None
        }
        return info
    
    def reset_listening_state(self):
        """Reset listening state"""
        self.is_listening = False
    
    def shutdown(self):
        """Shutdown the assistant"""
        try:
            self.data_manager.save_all_data()
            self.running = False
            return "Data saved successfully. Goodbye!"
        except Exception as e:
            return f"Error during shutdown: {str(e)}"

# Audio processor class for Streamlit
class StreamlitAudioProcessor:
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

# Main app function
def main():
    # Page configuration
    st.set_page_config(
        page_title="NexusAI Voice Assistant",
        page_icon="🤖",
        layout="wide"
    )

    # Initialize session state
    if "nexus_ai" not in st.session_state:
        if NEXUS_BACKEND_AVAILABLE:
            try:
                st.session_state.nexus_ai = StreamlitNexusAI()
                st.session_state.backend_status = "✅ Backend Loaded"
            except Exception as e:
                st.session_state.nexus_ai = None
                st.session_state.backend_status = f"❌ Backend Error: {str(e)}"
        else:
            st.session_state.nexus_ai = None
            st.session_state.backend_status = f"❌ Backend Not Available: {IMPORT_ERROR}"
    
    if "audio_processor" not in st.session_state:
        st.session_state.audio_processor = StreamlitAudioProcessor()
    
    if "voice_text" not in st.session_state:
        st.session_state.voice_text = ""
    
    if "listening_timeout" not in st.session_state:
        st.session_state.listening_timeout = None

    # Custom CSS (same as before)
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
        
        .status-card {
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            text-align: center;
        }
        
        .status-success {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .status-error {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
            color: white;
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
        
        .system-info {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 5px;
            border-left: 4px solid #6c63ff;
        }
        </style>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown("### 🔧 System Status")
        st.markdown(f"**Backend:** {st.session_state.backend_status}")
        
        if st.session_state.nexus_ai:
            system_info = st.session_state.nexus_ai.get_system_info()
            st.markdown("### 📊 System Info")
            st.json(system_info)
            
            if st.button("🔄 Reset Listening State"):
                st.session_state.nexus_ai.reset_listening_state()
                st.success("Listening state reset!")
            
            if st.button("💾 Save Data"):
                try:
                    st.session_state.nexus_ai.data_manager.save_all_data()
                    st.success("Data saved successfully!")
                except Exception as e:
                    st.error(f"Error saving data: {e}")
            
            if st.button("🛑 Shutdown Assistant"):
                shutdown_msg = st.session_state.nexus_ai.shutdown()
                st.info(shutdown_msg)
        
        st.markdown("### 🕓 Conversation History")
        if st.button("🗑️ Clear History"):
            if st.session_state.nexus_ai:
                st.session_state.nexus_ai.conversation_history = []
            st.rerun()

    # Main content
    st.markdown('<h1 class="main-header">🤖 NexusAI Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">🎙️ Your Intelligent Voice Companion</p>', unsafe_allow_html=True)

    # Check if we're in a proper Streamlit session
    if not is_streamlit_running():
        st.markdown("""
        <div class="status-card status-error">
            <h3>⚠️ Incorrect Launch Method</h3>
            <p>Please run this app using the command:</p>
            <code>streamlit run main.py</code>
            <p>Do not use <code>python -u</code> to run Streamlit applications.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # Backend status display
    if not NEXUS_BACKEND_AVAILABLE:
        st.markdown(f"""
        <div class="status-card status-error">
            <h3>❌ NexusAI Backend Not Available</h3>
            <p>Missing required modules: {IMPORT_ERROR}</p>
            <p>Please ensure all NexusAI components are present:</p>
            <ul>
                <li>config.py</li>
                <li>nlp_processor.py</li>
                <li>data_manager.py</li>
                <li>audio_handler.py</li>
                <li>command_processor.py</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        return
    
    if not st.session_state.nexus_ai:
        st.error("Failed to initialize NexusAI backend. Check the sidebar for details.")
        return

    # Voice input section
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if WEBRTC_AVAILABLE:
            try:
                st.markdown("### 🎤 Voice Input")
                
                audio_ctx = webrtc_streamer(
                    key="nexus-audio",
                    mode=WebRtcMode.RECVONLY,
                    audio_frame_callback=st.session_state.audio_processor.recv,
                    media_stream_constraints={"audio": True, "video": False},
                    async_processing=True,
                )
                
                if audio_ctx.state.playing:
                    st.markdown('<div class="status-card status-success">🎧 Listening... Click "Stop & Process" when done speaking.</div>', unsafe_allow_html=True)
                    
                    if st.button("🔴 Stop & Process Audio", key="stop_audio"):
                        transcribed_text = st.session_state.audio_processor.get_text()
                        if transcribed_text and transcribed_text not in ["Sorry, I couldn't understand that.", None]:
                            st.session_state.voice_text = transcribed_text
                            st.session_state.audio_processor.clear_buffer()
                            st.rerun()
                
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
    
    if final_input and st.session_state.nexus_ai:
        # Clear voice text after processing
        if st.session_state.voice_text:
            st.session_state.voice_text = ""
        
        # Process input using NexusAI backend
        with st.spinner("Processing with NexusAI..."):
            response, should_exit = st.session_state.nexus_ai.process_input(final_input)
        
        if should_exit:
            st.warning("Assistant requested shutdown.")
            st.session_state.nexus_ai.shutdown()
        
        st.rerun()

    # Display conversation
    if st.session_state.nexus_ai and st.session_state.nexus_ai.conversation_history:
        st.markdown("### 💭 Conversation")
        for msg in st.session_state.nexus_ai.conversation_history[-10:]:  # Show last 10 messages
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
    
    # Auto-refresh for listening state timeout
    if st.session_state.nexus_ai and st.session_state.nexus_ai.is_listening:
        # Auto-reset listening state after 10 seconds (simulated)
        if st.session_state.listening_timeout is None:
            st.session_state.listening_timeout = time.time() + 10
        elif time.time() > st.session_state.listening_timeout:
            st.session_state.nexus_ai.reset_listening_state()
            st.session_state.listening_timeout = None
            st.rerun()

if __name__ == "__main__":
    main()