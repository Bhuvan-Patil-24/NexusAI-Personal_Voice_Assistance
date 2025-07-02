# 🎤 NexusAI - Advanced Voice Assistant

NexusAI is a sophisticated, modular voice assistant built with Python that combines speech recognition, natural language processing, and a sleek user interface. It's designed to help you interact with your computer using natural voice commands while providing a modern, customizable experience.

---

## ✨ Features

- 🎙️ **Voice Recognition** – Interact with your computer using natural speech
- 🧠 **Advanced NLP** – Understand complex commands
- 🚀 **App Launcher** – Open applications via voice
- 🔔 **Reminder System** – Set and manage reminders
- 📝 **Text Summarization** – Summarize content using Google’s Gemini AI
- 🌐 **Web Integration** – Search the web and access information
- 🎨 **Modern UI** – Sleek, animated interface built with Streamlit
- 🧩 **Modular Architecture** – Easily extend with new features

---

## 🏗️ Project Structure

```
.
├── components/               # Core functionality modules
│   ├── audio\_handler.py      # Speech recognition and synthesis
│   ├── command\_processor.py  # Process and execute commands
│   ├── config.py             # Configuration settings
│   ├── data\_manager.py       # Data persistence
│   └── nlp\_processor.py      # Natural language processing
├── css/
│   └── style.css             # UI styling and animations
├── features/                 # Extended functionality
│   ├── appLauncher.py        # Application launching
│   ├── reminder\_sys.py       # Reminder management
│   ├── summarizer.py         # Text summarization
│   └── ui\_controller.py      # UI management
├── main.py                   # Streamlit UI entry point
├── nexus\_ai.py               # Core assistant logic
└── requirements.txt          # Project dependencies
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Windows OS (for full app launcher functionality)

---

### Installation

1. **Clone the repository**

```bash
   git clone https://github.com/yourusername/NexusAI.git
   cd NexusAI
```

2. **Install dependencies**

```bash
   pip install -r requirements.txt
```

3. **Download required NLP models**

```bash
   python -m nltk.downloader punkt stopwords wordnet averaged_perceptron_tagger maxent_ne_chunker words
   python -m spacy download en_core_web_sm
```

4. **Create a `.env` file in the project root with the following:**

```bash
   WAKE_WORD=nexus
   WEATHER_API_KEY=your_api_key_here
```
---

### Running NexusAI

**Start the Streamlit UI:**

```bash
streamlit run main.py
```

**Or run the console version:**

```bash
python nexus_ai.py
```

---

## 🗣️ Usage

Activate NexusAI by saying the wake word **"Nexus"** followed by your command, for example:

* `Nexus, what time is it?`
* `Nexus, open Chrome`
* `Nexus, remind me to check emails in 30 minutes`
* `Nexus, what's the weather like today?`
* `Nexus, summarize this article for me`

---

## 🧩 Extending NexusAI

NexusAI’s modular architecture makes it easy to add new features:

1. Create a new module in the `features/` directory.
2. Import and integrate it in `command_processor.py`.
3. Add relevant intent patterns in `config.py`.

---

## 🎨 Customizing the UI

To customize the appearance of the Streamlit interface, edit:

```
css/style.css
```

---

## 📋 Dependencies

* **SpeechRecognition** – Voice recognition
* **pyttsx3** – Text-to-speech
* **nltk & spacy** – Natural language processing
* **streamlit** – Web interface
* **google-generativeai** – AI-powered summarization
* *(And more – see `requirements.txt`)*

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---
