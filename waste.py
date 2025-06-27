import streamlit as st
import time
from datetime import datetime
from threading import Thread, Event
import queue
# Import your existing modules
try:
    from config import WAKE_WORD
    from components.nlp_processor import NLPProcessor
    from components.data_manager import DataManager
    from components.audio_handler import AudioHandler
    from components.command_processor import CommandProcessor
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

# Custom CSS for modern dark theme with integrated animation


def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Load the CSS file
load_css("css/style.css")

# Initialize session state variables


def initialize_session_state():
    if 'nexus_initialized' not in st.session_state:
        st.session_state.nexus_initialized = False
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'is_listening' not in st.session_state:
        st.session_state.is_listening = False
    if 'is_speaking' not in st.session_state:
        st.session_state.is_speaking = False
    if 'wake_word' not in st.session_state:
        st.session_state.wake_word = WAKE_WORD.lower()
    if 'last_processed_input' not in st.session_state:
        st.session_state.last_processed_input = ""
    if 'running' not in st.session_state:
        st.session_state.running = True
    if 'message_queue' not in st.session_state:
        st.session_state.message_queue = queue.Queue()
    if 'system_info_visible' not in st.session_state:
        st.session_state.system_info_visible = False
    if 'speaking_event' not in st.session_state:
        st.session_state.speaking_event = Event()


def initialize_nexus_components():
    try:
        print("Initializing NexusAI components...")
        with st.spinner("Initializing NexusAI components..."):
            st.session_state.data_manager = DataManager()
            st.session_state.nlp_processor = NLPProcessor()
            st.session_state.audio_handler = AudioHandler()
            st.session_state.command_processor = CommandProcessor(
                st.session_state.nlp_processor,
                st.session_state.data_manager
            )
            st.session_state.nexus_initialized = True
            print("NexusAI initialization complete!")
            return True
    except Exception as e:
        st.error(f"Failed to initialize NexusAI: {e}")
        return False


def safe_speak(text):
    """Thread-safe speaking function"""
    def speak_in_thread():
        try:
            st.session_state.is_speaking = True
            st.session_state.speaking_event.set()
            # Add a small delay to ensure UI updates
            time.sleep(0.1)
            st.session_state.audio_handler.speak(text)
            # Keep speaking state for a bit longer for visual feedback
            time.sleep(0.5)
        except Exception as e:
            print(f"Error with text-to-speech: {e}")
        finally:
            st.session_state.is_speaking = False
            st.session_state.speaking_event.clear()

    # Run speaking in a separate thread to avoid blocking
    Thread(target=speak_in_thread, daemon=True).start()


def shutdown():
    st.session_state.running = False

    # Save all data before shutdown
    try:
        st.session_state.data_manager.save_all_data()
        print("Data saved to DB.")
    except Exception as e:
        print(f"Error saving data: {e}")

    safe_speak("Shutting Down.")
    print("NexusAI shutdown complete.")


def listen_for_voice():
    """Background voice listening function"""
    if not st.session_state.get('voice_thread_started', False):
        st.session_state.voice_thread_started = True

        def voice_loop():
            print("Voice listening thread started...")
            while st.session_state.nexus_initialized and st.session_state.running:
                try:
                    # Listen for audio input
                    print("Listening for audio...")
                    audio_input = st.session_state.audio_handler.listen()

                    if audio_input:
                        print(f"Audio received: {audio_input}")
                        # Check for wake word or if already listening
                        if st.session_state.wake_word in audio_input.lower() or st.session_state.is_listening:
                            print("Wake word detected or already listening")
                            # Queue the message for processing
                            st.session_state.message_queue.put({
                                'type': 'voice',
                                'content': audio_input,
                                'timestamp': datetime.now().strftime("%H:%M:%S")
                            })

                            # Set listening state for follow-up commands
                            st.session_state.is_listening = True

                            # Reset listening state after a delay
                            def reset_listening():
                                time.sleep(10)
                                st.session_state.is_listening = False
                                print("Listening state reset")

                            Thread(target=reset_listening, daemon=True).start()

                except Exception as e:
                    print(f"Error in voice listening: {e}")
                    continue
                except KeyboardInterrupt:
                    print("\nShutting down voice listener...")
                    break

                time.sleep(0.1)  # Small delay to prevent excessive CPU usage

        # Start voice listening thread
        Thread(target=voice_loop, daemon=True).start()
        print("Voice listening thread initialized")


def process_queued_messages():
    """Process messages from the queue"""
    processed_any = False

    while not st.session_state.message_queue.empty():
        try:
            message = st.session_state.message_queue.get_nowait()

            # Add user message
            st.session_state.chat_history.append({
                'type': 'user',
                'message': message['content'],
                'timestamp': message['timestamp']
            })

            # Process command
            response, should_exit = st.session_state.command_processor.process_command(
                message['content'])

            # Add assistant response
            st.session_state.chat_history.append({
                'type': 'assistant',
                'message': response,
                'timestamp': datetime.now().strftime("%H:%M:%S")
            })

            # Speak response
            safe_speak(response)

            if should_exit:
                shutdown()
                st.success("NexusAI has been shut down.")

            processed_any = True

        except queue.Empty:
            break
        except Exception as e:
            print(f"Error processing queued message: {e}")

    return processed_any


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
            safe_speak(response)

            if should_exit:
                st.session_state.running = False
                st.success("NexusAI has been shut down.")

            # Clear the processed input
            st.session_state.last_processed_input = text_input

        except Exception as e:
            st.error(f"Error processing text input: {e}")


def get_system_info():
    """Get current system information"""
    try:
        info = {
            'is_listening': st.session_state.get('is_listening', False),
            'is_speaking': st.session_state.get('is_speaking', False),
            'wake_word': st.session_state.get('wake_word', 'nexus'),
            'running': st.session_state.get('running', False),
            'chat_messages': len(st.session_state.get('chat_history', [])),
            'current_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'nexus_initialized': st.session_state.get('nexus_initialized', False),
            'voice_thread_started': st.session_state.get('voice_thread_started', False)
        }

        # Add data manager info if available
        if st.session_state.get('nexus_initialized', False):
            try:
                if hasattr(st.session_state.data_manager, 'get_storage_info'):
                    info['data_info'] = st.session_state.data_manager.get_storage_info()
            except Exception as e:
                info['data_info_error'] = str(e)

        return info
    except Exception as e:
        return {'error': str(e)}


def toggle_system_info():
    """Toggle system info visibility"""
    st.session_state.system_info_visible = not st.session_state.system_info_visible


def main():
    # Initialize session state
    initialize_session_state()

    # Show loading animation while initializing
    if not st.session_state.nexus_initialized:
        # Initialize components
        if not initialize_nexus_components():
            st.stop()

        # Refresh to show main UI
        st.rerun()

    # Process any queued messages
    if process_queued_messages():
        st.rerun()

    # Start voice listening
    listen_for_voice()

    # Determine animation classes - now based on speaking instead of listening
    speaking_class = "listening" if st.session_state.is_speaking else ""

    # Main header
    st.markdown('<h1 class="main-header">NexusAI</h1>', unsafe_allow_html=True)

    # Central animation - updated to show animation when speaking
    st.markdown(f"""
        <div id="main">
        <div id="myCircle">
        <div id="mainCircle">
            <div class="circle {speaking_class}"></div>
            <div class="circle1 {speaking_class}"></div>
            <div id="mainContent">
                <ul class="bars one {speaking_class}">
                    <li></li>
                    <li></li>
                </ul>
                <ul class="bars two {speaking_class}">
                    <li></li>
                    <li></li>
                    <li></li>
                </ul>
                <ul class="bars three {speaking_class}">
                    <li></li>
                    <li></li>
                </ul>
                <ul class="bars four {speaking_class}">
                    <li></li>
                    <li></li>
                    <li></li>
                </ul>
                </div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    # Welcome message (only once)
    if not st.session_state.get('welcome_spoken', False):
        welcome_msg = "Hello! I'm NexusAI, your personal voice assistant. Say 'Nexus' followed by your command to wake me up."
        safe_speak(welcome_msg)
        st.session_state.welcome_spoken = True

    # Chat history display
    st.subheader("💬Conversation")

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
                Say "Nexus" to wake me up...
            </div>
            """, unsafe_allow_html=True)

    # Bottom section with text input and system info button
    st.markdown("<br><br>", unsafe_allow_html=True)

    # Create columns for the bottom section
    col1, col2 = st.columns([8, 2])

    with col1:
        # Text input for chat
        if 'input_key' not in st.session_state:
            st.session_state.input_key = 0

        text_input = st.text_input(
            "Chat with Nexus..",
            key=f"text_input_{st.session_state.input_key}",
            placeholder="Type your command or question here...",
            label_visibility="collapsed"
        )

        # Process text input
        if text_input and text_input != st.session_state.last_processed_input:
            process_text_input(text_input)
            # Increment key to create new widget and clear input
            st.session_state.input_key += 1
            st.rerun()

    with col2:
        # System info toggle button
        if st.button("📊 System Info", help="Toggle system information display"):
            st.session_state.system_info_visible = not st.session_state.system_info_visible

    # Display system info if toggled on
    if st.session_state.system_info_visible:
        st.markdown("---")
        st.subheader("📊 System Information")

        system_info = get_system_info()

        # Display system info in a nice format
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Status", "Running" if system_info.get(
                'running') else "Stopped")
            st.metric("Listening", "Yes" if system_info.get(
                'is_listening') else "No")
            st.metric("Speaking", "Yes" if system_info.get(
                'is_speaking') else "No")

        with col2:
            st.metric("Wake Word", system_info.get('wake_word', 'Unknown'))
            st.metric("Chat Messages", system_info.get('chat_messages', 0))
            st.metric("Initialized", "Yes" if system_info.get(
                'nexus_initialized') else "No")

        with col3:
            st.metric("Voice Thread", "Active" if system_info.get(
                'voice_thread_started') else "Inactive")
            st.write(
                f"**Current Time:** {system_info.get('current_time', 'Unknown')}")

        # Show detailed info in expandable section
        with st.expander("System Information"):
            st.json(system_info)

    # Auto-refresh every 1 second to update the UI and check for speaking state
    if st.session_state.get('nexus_initialized', False):
        time.sleep(1)
        st.rerun()


if __name__ == "__main__":
    main()
