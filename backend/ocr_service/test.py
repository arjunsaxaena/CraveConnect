from dotenv import load_dotenv
import google.generativeai as genai
import os

def main():
    # Load environment variables from .env file
    load_dotenv()

    # Get the API key from environment variables
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in your .env file.")

    # Configure the Google Generative AI client with your API key
    genai.configure(api_key=api_key)

    # List and print all available models with their supported generation methods
    models = genai.list_models()
    print("Available models and their supported generation methods:")
    for model in models:
        print(f"- {model.name}: {model.supported_generation_methods}")

if __name__ == "__main__":
    main()
