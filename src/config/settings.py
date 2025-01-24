import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Environment configurations
GROQ_API_KEY = os.getenv("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")
GROQ_API_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"  # Replace with actual endpoint
SENTIMENT_API_URL = "https://api.groq.com/openai/v1/chat/completions"