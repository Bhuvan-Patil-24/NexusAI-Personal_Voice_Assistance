import streamlit as st
import speech_recognition as sr
import numpy as np
from datetime import datetime
import time
import threading
import json
import os
from typing import Dict, Any, Optional, Tuple

# Import statements with fallbacks
try:
    from streamlit_webrtc import webrtc_streamer, WebRtcMode
    import av
    WEBRTC_AVAILABLE = True
except ImportError:
    WEBRTC_AVAILABLE = False

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

try:
    import wikipedia
    WIKIPEDIA_AVAILABLE = True
except ImportError:
    WIKIPEDIA_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Configuration
WAKE_WORD = "nexus"

class DataManager:
    """Manages conversation data and settings"""
    def __init__(self):
        self.data_file = "nexus_data.json"
        self.data = self.load_data()
    
    def load_data(self) -> Dict[str, Any]:
        """Load data from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            "conversations": [],
            "user_preferences": {},
            "settings": {"wake_word": WAKE_WORD}
        }
    
    def save_data(self):
        """Save data to JSON file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            st.error(f"Error saving data: {e}")
    
    def add_conversation(self, user_input: str, response: str):
        """Add conversation to history"""
        self.data["conversations"].append({
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "assistant": response
        })
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get storage information"""
        return {
            "total_conversations": len(self.data["conversations"]),
            "file_size": os.path.getsize(self.data_file) if os.path.exists(self.data_file) else 0
        }

class NLPProcessor:
    """Processes natural language input"""
    def __init__(self):
        self.wake_word = WAKE_WORD.lower()
    
    def extract_intent(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """Extract intent and entities from text"""
        text_lower = text.lower()
        
        # Remove wake word if present
        if self.wake_word in text_lower:
            text_lower = text_lower.replace(self.wake_word, "").strip()
        
        # Intent classification
        if any(word in text_lower for word in ["hello", "hi", "hey", "greetings"]):
            return "greeting", {}
        elif any(word in text_lower for word in ["bye", "goodbye", "exit", "quit"]):
            return "farewell", {}
        elif any(word in text_lower for word in ["time", "clock"]):
            return "time_query", {}
        elif any(word in text_lower for word in ["date", "today"]):
            return "date_query", {}
        elif any(word in text_lower for word in ["weather", "temperature"]):
            return "weather_query", {}
        elif any(word in text_lower for word in ["search", "find", "look up"]):
            query = text_lower.replace("search", "").replace("find", "").replace("look up", "").strip()
            return "search_query", {"query": query}
        elif "wikipedia" in text_lower or "wiki" in text_lower:
            topic = text_lower.replace("wikipedia", "").replace("wiki", "").strip()
            return "wikipedia_query", {"topic": topic}
        else:
            return "general_query", {"text": text}

class AudioHandler:
    """Handles audio input and output"""
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.tts_engine = None
        
        if TTS_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 150)
            except:
                self.tts_engine = None
    
    def speak(self, text: str):
        """Convert text to speech"""
        if self.tts_engine:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except:
                pass  # Fallback to text only
    
    def transcribe_audio(self, audio_data) -> Optional[str]:
        """Transcribe audio data to text"""
        try:
            if hasattr(audio_data, 'get_wav_data'):
                # speech_recognition AudioData object
                return self.recognizer.recognize_google(audio_data)
            else:
                # Raw audio bytes
                audio_obj = sr.AudioData(audio_data, 16000, 2)
                return self.recognizer.recognize_google(audio_obj)
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand that."
        except sr.RequestError as e:
            return f"Speech recognition error: {e}"
        except Exception as e:
            return f"Error processing audio: {e}"

class CommandProcessor:
    """Processes commands and generates responses"""
    def __init__(self, nlp_processor: NLPProcessor, data_manager: DataManager):
        self.nlp_processor = nlp_processor
        self.data_manager = data_manager
    
    def process_command(self, user_input: str) -> Tuple[str, bool]:
        """Process user command and return response and exit flag"""
        intent, entities = self.nlp_processor.extract_intent(user_input)
        
        response = ""
        should_exit = False
        
        if intent == "greeting":
            response = "Hello! I'm Nexus, your AI assistant. How can I help you today?"
        
        elif intent == "farewell":
            response = "Goodbye! It was nice talking with you. Have a great day!"
            should_exit = True
        
        elif intent == "time_query":
            current_time = datetime.now().strftime("%H:%M:%S")
            response = f"The current time is {current_time}."
        
        elif intent == "date_query":
            current_date = datetime.now().strftime("%B %d, %Y")
            response = f"Today's date is {current_date}."
        
        elif intent == "weather_query":
            response = "I don't have access to real-time weather data, but I'd be happy to help you find a weather service!"
        
        elif intent == "search_query":
            query = entities.get("query", "")
            if query:
                response = f"I would search for '{query}' but I don't have internet access right now. Try asking me something else!"
            else:
                response = "What would you like me to search for?"
        
        elif intent == "wikipedia_query":
            topic = entities.get("topic", "")
            if WIKIPEDIA_AVAILABLE and topic:
                try:
                    summary = wikipedia.summary(topic, sentences=2)
                    response = f"Here's what I found about {topic}: {summary}"
                except wikipedia.exceptions.DisambiguationError as e:
                    response = f"There are multiple topics for '{topic}'. Could you be more specific? Options include: {', '.join(e.options[:3])}"
                except wikipedia.exceptions.PageError:
                    response = f"I couldn't find information about '{topic}' on Wikipedia."
                except:
                    response = f"I had trouble accessing Wikipedia information about '{topic}'."
            else:
                response = "What topic would you like me to look up on Wikipedia?"
        
        else:
            response = f"I heard you say: '{user_input}'. I'm still learning, but I'm here to help! What would you like to know?"
        
        # Save conversation
        self.data_manager.add_conversation(user_input, response)
        
        return response, should_exit

class AudioProcessor:
    """Processes audio streams for Streamlit WebRTC"""
    def __init__(self):
        self.audio_buffer = b""
        self.sample_rate = 16000
        self.audio_handler = AudioHandler()

    def recv(self, frame):
        """Receive audio frame from WebRTC"""
        if hasattr(frame, 'to_ndarray'):
            audio = frame.to_ndarray().flatten().astype(np.int16).tobytes()
            self.audio_buffer += audio
        return frame

    def get_text(self) -> Optional[str]:
        """Get transcribed text from audio buffer"""
        if not self.audio_buffer:
            return None
        
        result = self.audio_handler.transcribe_audio(self.audio_buffer)
        return result

    def clear_buffer(self):
        """Clear the audio buffer"""
        self.audio_buffer = b""

class NexusAI:
    """Main NexusAI assistant class for Streamlit"""
    def __init__(self):
        # Initialize core components
        self.data_manager = DataManager()
        self.nlp_processor = NLPProcessor()
        self.audio_handler = AudioHandler()
        self.command_processor = CommandProcessor(
            self.nlp_processor, 
            self.data_manager
        )
        
        # Assistant state
        self.wake_word = WAKE_WORD.lower()
    
    def process_input(self, user_input: str) -> str:
        """Process user input and return response"""
        response, _ = self.command_processor.process_command(user_input)
        return response
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            'wake_word': self.wake_word,
            'data_info': self.data_manager.get_storage_info(),
            'components_loaded': {
                'webrtc': WEBRTC_AVAILABLE,
                'tts': TTS_AVAILABLE,
                'wikipedia': WIKIPEDIA_AVAILABLE,
                'requests': REQUESTS_AVAILABLE
            }
        }

# Check if we're running in a proper Streamlit context
def is_streamlit_running():
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx() is not None
    except:
        return False

def main():
    """Main Streamlit application"""
    # Page configuration
    st.set_page_config(
        page_title="Nexus AI Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize session state
    if "nexus_ai" not in st.session_state:
        st.session_state.nexus_ai = NexusAI()
    
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
        
        .info-box {
            background-color: #e6f3ff;
            color: #0066cc;
            padding: 1rem;
            border-radius: 5px;
            border-left: 4px solid #0066cc;
            margin: 1rem 0;
        }
        </style>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-title">🤖 Nexus AI Control Panel</div>', unsafe_allow_html=True)
        
        # System Info
        with st.expander("⚙️ System Information"):
            system_info = st.session_state.nexus_ai.get_system_info()
            st.json(system_info)
        
        # Conversation History
        st.markdown('<div class="sidebar-title">🕓 Conversation History</div>', unsafe_allow_html=True)
        
        if st.button("🗑️ Clear History"):
            st.session_state.history = []
            st.session_state.nexus_ai.data_manager.data["conversations"] = []
            st.rerun()
        
        if st.button("💾 Save Data"):
            st.session_state.nexus_ai.data_manager.save_data()
            st.success("Data saved!")
        
        # Display recent conversations
        for i, msg in enumerate(reversed(st.session_state.history[-10:])):
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
            <code>streamlit run nexus_app.py</code>
            <p>Do not use <code>python -u</code> to run Streamlit applications.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # Component status
    status_cols = st.columns(4)
    with status_cols[0]:
        st.metric("🎤 WebRTC", "✅ Available" if WEBRTC_AVAILABLE else "❌ Missing")
    with status_cols[1]:
        st.metric("🔊 TTS", "✅ Available" if TTS_AVAILABLE else "❌ Missing")
    with status_cols[2]:
        st.metric("📚 Wikipedia", "✅ Available" if WIKIPEDIA_AVAILABLE else "❌ Missing")
    with status_cols[3]:
        st.metric("🌐 Requests", "✅ Available" if REQUESTS_AVAILABLE else "❌ Missing")

    # Voice input section
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if WEBRTC_AVAILABLE:
            try:
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
            st.markdown("""
            <div class="info-box">
                <h4>🎤 Voice Input Unavailable</h4>
                <p>Install streamlit-webrtc for voice input support:</p>
                <code>pip install streamlit-webrtc</code>
            </div>
            """, unsafe_allow_html=True)

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
        
        # Generate response using NexusAI
        with st.spinner("🤔 Thinking..."):
            response = st.session_state.nexus_ai.process_input(final_input)
        
        reply_time = datetime.now().strftime("%H:%M:%S")
        
        st.session_state.history.append({
            "role": "Nexus", 
            "message": response, 
            "time": reply_time
        })
        
        # TTS for response (if available)
        if TTS_AVAILABLE:
            try:
                st.session_state.nexus_ai.audio_handler.speak(response)
            except:
                pass  # Silent fail for TTS
        
        st.rerun()

    # Display conversation
    st.markdown("### 💭 Conversation")
    
    if not st.session_state.history:
        st.markdown("""
        <div class="info-box">
            <h4>👋 Welcome to Nexus AI!</h4>
            <p>Start a conversation by typing a message or using voice input. Try saying:</p>
            <ul>
                <li>"Hello Nexus"</li>
                <li>"What time is it?"</li>
                <li>"Tell me about Python"</li>
                <li>"Search for artificial intelligence"</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    for msg in st.session_state.history[-10:]:  # Show last 10 messages
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

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🤖 Nexus AI Assistant - Powered by Streamlit</p>
        <p><small>Say "Nexus" followed by your command for voice activation</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()