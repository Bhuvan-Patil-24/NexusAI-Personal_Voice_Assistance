import streamlit as st
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()
WAKE_WORD = os.getenv("WAKE_WORD")

# Import your existing modules
try:
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



def listen_for_voice():
    while st.session_state.nexus_initialized and st.session_state.running:
        try:
            # Listen for audio input
            audio_input = st.session_state.audio_handler.listen()

            if audio_input:
                # Check for wake word or if already listening
                if st.session_state.wake_word in audio_input.lower() or st.session_state.is_listening:
                    # Process command
                    response, should_exit = st.session_state.command_processor.process_command(
                        audio_input)

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

        except Exception as e:
            print(f"Error in Listening: {e}")
            # traceback.print_exc()
            st.session_state.audio_handler.speak(
                "Sorry, I encountered an error. Please try again.")
        except KeyboardInterrupt:
            print("\nShutting down NexusAI...")
            shutdown()
            break


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
#--------(yaha se rerun)
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
#------(yaha tak)
    # Welcome message (only once)
    if not st.session_state.get('welcome_spoken', False):
        welcome_msg = "Hello! I'm NexusAI, your personal voice assistant. Say 'Nexus' followed by your command to wake me up."
        st.session_state.audio_handler.speak(welcome_msg)
        # st.session_state.is_speaking = False
        st.session_state.welcome_spoken = True
        # st.rerun()

    listen_for_voice()


if __name__ == "__main__":
    main()
