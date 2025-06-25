from config import GEMINI_API_KEY
import google.generativeai as genai

# Setup API key
genai.configure(api_key=GEMINI_API_KEY)

# for model in genai.list_models():
#     print(f"Model: {model.name}, Description: {model.description}")

# Load Gemini Pro model
model = genai.GenerativeModel('gemini-2.5-flash')

# Ask a prompt
prompt = input("You: ")

response = model.generate_content(prompt)

# Show response
print("Gemini:", response.text)
