import streamlit as st
import time
from datetime import datetime
from threading import Thread
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


def shutdown():
    st.session_state.running = False

    # Save all data before shutdown
    try:
        st.session_state.data_manager.save_all_data()
        print("Data saved to DB.")
    except Exception as e:
        print(f"Error saving data: {e}")

    st.session_state.audio_handler.speak("Shutting Down.")
    print("NexusAI shutdown complete.")
    st.stop()


def listen_for_voice():
    while st.session_state.nexus_initialized and st.session_state.running:
        try:
            # Listen for audio input
            audio_input = st.session_state.audio_handler.listen()

            if audio_input:
                # Check for wake word or if already listening
                if st.session_state.wake_word in audio_input.lower() or st.session_state.is_listening:
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
                        shutdown()
                        st.success("NexusAI has been shut down.")

                    # Set listening state for follow-up commands
                    st.session_state.is_listening = True
                    st.rerun()
                    # Reset listening state after a delay

                    def reset_listening():
                        time.sleep(10)
                        st.session_state.is_listening = False

                    Thread(target=reset_listening, daemon=True).start()

        except Exception as e:
            print(f"Error in Listening: {e}")
            # traceback.print_exc()
            st.session_state.audio_handler.speak(
                "Sorry, I encountered an error. Please try again.")
        except KeyboardInterrupt:
            print("\nShutting down NexusAI...")
            shutdown()
            break


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
                st.session_state.running = False
                st.success("NexusAI has been shut down.")

        except Exception as e:
            st.error(f"Error processing text input: {e}")


def get_system_info():
    try:
        info = {
            'is_listening': st.session_state.get('is_listening', False),
            'wake_word': st.session_state.get('wake_word', 'nexus'),
            'running': st.session_state.get('runnning', False),
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
        return {'Error': str(e)}


def main():
    print("Initializing session...")
    # Initialize session state
    initialize_session_state()

    # Show loading animation while initializing
    if not st.session_state.nexus_initialized:
        # Initialize components
        if not initialize_nexus_components():
            st.stop()

        # Refresh to show main UI
        st.rerun()

    # Determine animation classes - now based on speaking instead of listening
    speaking_class = "speaking" if st.session_state.is_speaking else ""

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
        st.session_state.audio_handler.speak(welcome_msg)
        st.session_state.welcome_spoken = True

    # Bottom section with text input and system info button
    st.markdown("<br><br>", unsafe_allow_html=True)

    col = st.columns([1, 2, 1])[1]

    with col:
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

    st.markdown("---")

    # Show detailed info in expandable section
    with st.expander("System Information"):
        st.json(get_system_info())
            
    listen_for_voice()


if __name__ == "__main__":
    main()
