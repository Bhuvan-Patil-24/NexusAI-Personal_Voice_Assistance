from .  import nexus_ai_data as d
import google.generativeai as genai


class GeminiSummarizer:
    def __init__(self, model_name='gemini-2.5-flash', temperature=0.4, top_p=1.0, top_k=40):
        # Setup API key
        genai.configure(api_key=d.config.GEMINI_API_KEY)

        # Initialize model
        self.model = genai.GenerativeModel(model_name)

        # Store generation config
        self.generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            top_p=top_p,
            top_k=top_k
        )

    def summarize(self, prompt):
        # Create the final prompt with instruction
        final_prompt = (
            f"Solve this maths expression and give directly the answer:\n\n{prompt}\n\n"
        )

        try:
            # Generate response
            response = self.model.generate_content(
                final_prompt,
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

if __name__=="__main__":
    ai = GeminiSummarizer()
    result = ai.summarize("100+200*4")
    print(result)