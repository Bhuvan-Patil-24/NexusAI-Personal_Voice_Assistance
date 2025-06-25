import streamlit as st
import time
from datetime import datetime

# Import your existing modules
try:
    from config import WAKE_WORD
    from nlp_processor import NLPProcessor
    from data_manager import DataManager
    from audio_handler import AudioHandler
    from command_processor import CommandProcessor
except ImportError as e:
    st.error(f"Missing required module: {e}")
    st.error("Please install missing packages and ensure all modules are available.")
    st.stop()

# Configure Streamlit page
st.set_page_config(
    page_title="NexusAI Voice Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern dark theme
st.markdown("""
<style>
    /* Global dark theme */
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        font-size: 3.5rem;
        font-weight: bold;
        color: #00ff88;
        text-shadow: 0 0 20px #00ff88;
        margin-bottom: 2rem;
        font-family: 'Arial', sans-serif;
    }
    
    /* Animation container */
    .animation-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 300px;
        margin: 2rem 0;
    }
    
    /* Pulsing animation */
    .pulse-animation {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        background: linear-gradient(45deg, #00ff88, #0066cc);
        animation: pulse 2s infinite;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 30px rgba(0, 255, 136, 0.5);
    }
    
    .pulse-animation.listening {
        animation: pulse-fast 0.5s infinite;
        background: linear-gradient(45deg, #ff6b6b, #ff8e8e);
        box-shadow: 0 0 30px rgba(255, 107, 107, 0.7);
    }
    
    @keyframes pulse {
        0% {
            transform: scale(1);
            opacity: 1;
        }
        50% {
            transform: scale(1.1);
            opacity: 0.7;
        }
        100% {
            transform: scale(1);
            opacity: 1;
        }
    }
    
    @keyframes pulse-fast {
        0% {
            transform: scale(1);
            opacity: 1;
        }
        50% {
            transform: scale(1.2);
            opacity: 0.6;
        }
        100% {
            transform: scale(1);
            opacity: 1;
        }
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #00ff88, #0066cc);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 1.5rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 255, 136, 0.4);
    }
    
    /* Text input styling */
    .stTextInput > div > div > input {
        background-color: #1a1a1a;
        color: #ffffff;
        border: 2px solid #00ff88;
        border-radius: 25px;
        padding: 0.75rem 1.5rem;
    }
    
    /* Chat message styling */
    .chat-message {
        background: linear-gradient(135deg, #1a1a1a, #2d2d2d);
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #00ff88;
    }
    
    .user-message {
        background: linear-gradient(135deg, #0066cc, #004499);
        border-left: 4px solid #0066cc;
        margin-left: 2rem;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #1a1a1a, #2d2d2d);
        border-left: 4px solid #00ff88;
        margin-right: 2rem;
    }
    
    /* Status indicator */
    .status-indicator {
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        z-index: 1000;
    }
    
    .status-listening {
        background: linear-gradient(45deg, #ff6b6b, #ff8e8e);
        color: white;
        animation: pulse 1s infinite;
    }
    
    .status-idle {
        background: linear-gradient(45deg, #00ff88, #0066cc);
        color: white;
    }
    
    .status-ready {
        background: linear-gradient(45deg, #ffaa00, #ff6600);
        color: white;
    }
    
    /* Hide streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2.5rem;
        }
        .pulse-animation {
            width: 120px;
            height: 120px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables


def initialize_session_state():
    """Initialize session state variables"""
    if 'nexus_initialized' not in st.session_state:
        st.session_state.nexus_initialized = False
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'is_listening' not in st.session_state:
        st.session_state.is_listening = False
    if 'wake_word' not in st.session_state:
        st.session_state.wake_word = WAKE_WORD.lower()
    if 'last_processed_input' not in st.session_state:
        st.session_state.last_processed_input = ""
    if 'voice_listening_enabled' not in st.session_state:
        st.session_state.voice_listening_enabled = True


def initialize_nexus_components():
    """Initialize NexusAI components"""
    try:
        with st.spinner("Initializing NexusAI components..."):
            # Initialize core components
            st.session_state.data_manager = DataManager()
            st.session_state.nlp_processor = NLPProcessor()
            st.session_state.audio_handler = AudioHandler()
            st.session_state.command_processor = CommandProcessor(
                st.session_state.nlp_processor,
                st.session_state.data_manager
            )

            st.session_state.nexus_initialized = True

            # Add welcome message
            welcome_msg = "Hello! I'm NexusAI, your personal voice assistant. Say 'Nexus' followed by your command, or type your message below."
            st.session_state.chat_history.append({
                'type': 'assistant',
                'message': welcome_msg,
                'timestamp': datetime.now().strftime("%H:%M:%S")
            })

            # Welcome speech
            try:
                st.session_state.audio_handler.speak(welcome_msg)
            except Exception as e:
                print(f"Error with text-to-speech: {e}")

            st.success("NexusAI initialized successfully!")
            time.sleep(1)
            return True

    except Exception as e:
        st.error(f"Failed to initialize NexusAI: {e}")
        return False


def listen_for_voice():
    """Listen for voice input"""
    if st.session_state.nexus_initialized and st.session_state.voice_listening_enabled:
        try:
            st.session_state.is_listening = True

            # Listen for audio input
            audio_input = st.session_state.audio_handler.listen()

            if audio_input:
                # Check for wake word or if already listening
                if st.session_state.wake_word in audio_input.lower():
                    # Add user message
                    st.session_state.chat_history.append({
                        'type': 'user',
                        'message': audio_input,
                        'timestamp': datetime.now().strftime("%H:%M:%S")
                    })

                    # Process command
                    response, should_exit = st.session_state.command_processor.process_command(
                        audio_input)

                    # Add assistant response
                    st.session_state.chat_history.append({
                        'type': 'assistant',
                        'message': response,
                        'timestamp': datetime.now().strftime("%H:%M:%S")
                    })

                    # Speak response
                    try:
                        st.session_state.audio_handler.speak(response)
                    except Exception as e:
                        print(f"Error with text-to-speech: {e}")

                    if should_exit:
                        st.session_state.voice_listening_enabled = False
                        st.success("NexusAI has been shut down.")

        except Exception as e:
            st.error(f"Error with voice recognition: {e}")
        finally:
            st.session_state.is_listening = False


def process_text_input(text_input):
    """Process text input from the chat box"""
    if text_input.strip() and st.session_state.nexus_initialized:
        try:
            # Add user message
            st.session_state.chat_history.append({
                'type': 'user',
                'message': text_input,
                'timestamp': datetime.now().strftime("%H:%M:%S")
            })

            # Process command
            response, should_exit = st.session_state.command_processor.process_command(
                text_input)

            # Add assistant response
            st.session_state.chat_history.append({
                'type': 'assistant',
                'message': response,
                'timestamp': datetime.now().strftime("%H:%M:%S")
            })

            # Speak response
            try:
                st.session_state.audio_handler.speak(response)
            except Exception as e:
                print(f"Error with text-to-speech: {e}")

            if should_exit:
                st.session_state.voice_listening_enabled = False
                st.success("NexusAI has been shut down.")

        except Exception as e:
            st.error(f"Error processing text input: {e}")


def get_system_info():
    """Get system information"""
    try:
        info = {
            'is_listening': st.session_state.get('is_listening', False),
            'wake_word': st.session_state.get('wake_word', 'nexus'),
            'voice_listening_enabled': st.session_state.get('voice_listening_enabled', False),
            'chat_messages': len(st.session_state.get('chat_history', [])),
            'current_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'nexus_initialized': st.session_state.get('nexus_initialized', False)
        }

        # Add data manager info if available
        if st.session_state.get('nexus_initialized', False):
            try:
                if hasattr(st.session_state.data_manager, 'get_storage_info'):
                    info['data_info'] = st.session_state.data_manager.get_storage_info()
            except:
                pass

        return info
    except Exception as e:
        return {'error': str(e)}


def main():
    # Initialize session state
    initialize_session_state()

    # Initialize NexusAI components if not already done
    if not st.session_state.nexus_initialized:
        if not initialize_nexus_components():
            st.stop()

    # Determine status
    if st.session_state.is_listening:
        status_class = "status-listening"
        status_text = "🎤 LISTENING"
        animation_class = "pulse-animation listening"
    elif st.session_state.voice_listening_enabled:
        status_class = "status-ready"
        status_text = "🟡 READY"
        animation_class = "pulse-animation"
    else:
        status_class = "status-idle"
        status_text = "💤 IDLE"
        animation_class = "pulse-animation"

    # Status indicator
    st.markdown(f"""
    <div class="status-indicator {status_class}">
        {status_text}
    </div>
    """, unsafe_allow_html=True)

    # Main header
    st.markdown('<h1 class="main-header">🤖 NexusAI</h1>',
                unsafe_allow_html=True)

    # Central animation
    st.markdown(f"""
    <div class="animation-container">
        <div class="{animation_class}">
            <span style="font-size: 3rem;">🤖</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Voice listening controls
    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_center:
        if st.session_state.voice_listening_enabled:
            if st.button("🎤 Listen for Voice Command", key="voice_btn", help="Click to listen for voice commands"):
                listen_for_voice()
                st.rerun()
        else:
            if st.button("🔄 Restart Voice Assistant", key="restart_btn", help="Restart the voice assistant"):
                st.session_state.voice_listening_enabled = True
                st.rerun()

    # Chat history display
    st.subheader("💬 Conversation History")

    # Create a container for chat messages
    chat_container = st.container()

    with chat_container:
        if st.session_state.chat_history:
            # Show messages in reverse order (newest first)
            # Show last 10 messages
            for message in reversed(st.session_state.chat_history[-10:]):
                message_class = "user-message" if message['type'] == 'user' else "assistant-message"
                icon = "👤" if message['type'] == 'user' else "🤖"

                st.markdown(f"""
                <div class="chat-message {message_class}">
                    <strong>{icon} {message['type'].title()}</strong> 
                    <span style="float: right; font-size: 0.8rem; opacity: 0.7;">{message['timestamp']}</span>
                    <br>
                    {message['message']}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="chat-message assistant-message">
                <strong>🤖 Assistant</strong>
                <br>
                Ready for your commands! Click the voice button above or type below.
            </div>
            """, unsafe_allow_html=True)

    # Bottom section with text input and buttons
    st.markdown("<br><br>", unsafe_allow_html=True)

    # Create columns for the bottom section
    col1, col2, col3 = st.columns([6, 1, 1])

    with col1:
        # Text input for chat
        text_input = st.text_input(
            "Type your message here...",
            key="text_input",
            placeholder="Type your command or question here...",
            label_visibility="collapsed"
        )

        # Process text input
        if text_input and text_input != st.session_state.last_processed_input:
            process_text_input(text_input)
            st.session_state.last_processed_input = text_input
            # Clear the input field
            st.session_state.text_input = ""
            st.rerun()

    with col2:
        # Clear history button
        if st.button("🗑️ Clear", help="Clear conversation history"):
            st.session_state.chat_history = []
            st.rerun()

    with col3:
        # System info button
        if st.button("ℹ️ Info", help="Show system information"):
            system_info = get_system_info()
            st.sidebar.json(system_info)
            st.sidebar.success("System information displayed!")


if __name__ == "__main__":
    main()
