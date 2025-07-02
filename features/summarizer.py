import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class GeminiSummarizer:
    def __init__(self, model_name='gemini-2.5-flash', temperature=0.4, top_p=1.0, top_k=40):
        # Setup API key
        genai.configure(api_key=GEMINI_API_KEY)

        # Initialize model
        self.model = genai.GenerativeModel(model_name)

        # Store generation config
        self.generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            top_p=top_p,
            top_k=top_k
        )

    def calculate(self, expr):
        # Create the final prompt with instruction
        final_prompt = (
            f"Solve this maths expression and give directly the answer and if the expression is inccorect just say incorect expresson dont give explaination:\n\n{expr}\n\n"
        )
        response = self.generate_response(final_prompt)
        if response:
            return f"The answer is {response}"
        else:
            return "Sorry, I am unable to solve this problem. Check your math problem."
    
    def summarize(self, prompt):
        # Create the final prompt with instruction
        final_prompt = (
            f"Summarize this in 2-3 lines, clear and meaningful:\n\n{prompt}\n\n"
        )
        return self.generate_response(final_prompt)

        
    def generate_response(self, prompt):
        try:
            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )

            # Safely extract text
            if response.candidates and response.candidates[0].content.parts:
                text_output = "".join(
                    part.text for part in response.candidates[0].content.parts)
                return text_output.strip()
            else:
                return None

        except Exception as e:
            print(f"Error generating summary: {e}")
            return None
