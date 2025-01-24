import openai

# Set up your API key
openai.api_key = "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"
def analyze_sentiment(text):
    """
    Uses an LLM to analyze the sentiment of a given text.
    """
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that classifies text sentiment as Positive, Neutral, or Negative."
        },
        {
            "role": "user",
            "content": f"Analyze the sentiment of the following text and classify it as Positive, Neutral, or Negative:\n\nText: \"{text}\"\n\nResponse should be one word: Positive, Neutral, or Negative."
        }
    ]
    
    try:
        response = openai.ChatCompletion.create(
            model="llama-3.1-8b-instant",  # Use "gpt-4" for better accuracy if available
            messages=messages,
            max_tokens=10,  # Keep it short since we only need one word
            temperature=0  # Deterministic output
        )
        sentiment = response['choices'][0]['message']['content'].strip()
        return sentiment
    except Exception as e:
        return f"Error: {e}"

# Test the sentiment analysis function
if __name__ == "__main__":
    sample_text = "The product is absolutely amazing! I love it."
    sentiment = analyze_sentiment(sample_text)
    print(f"Sentiment of the text: {sentiment}")
