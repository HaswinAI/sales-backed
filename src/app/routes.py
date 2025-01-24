from flask import Blueprint, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv
from textblob import TextBlob
import speech_recognition as sr
import pyttsx3
import pandas as pd
from datetime import datetime

# Load environment variables
load_dotenv()

# Blueprints
app_routes = Blueprint("app_routes", __name__)

# API details
SENTIMENT_API_URL = os.getenv("SENTIMENT_API_URL")
CHATBOT_API_URL = os.getenv("CHATBOT_API_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = os.getenv("GROQ_API_URL")  # Added for Groq API
HEADERS = {"Authorization": f"Bearer {GROQ_API_KEY}"}

# Conversation log file
log_file = "conversation_log.xlsx"

# ---------- Shared Utility Functions ----------

def analyze_sentiment_text(text):
    """Analyze sentiment using TextBlob."""
    blob = TextBlob(text)
    score = blob.sentiment.polarity
    if score > 0.1:
        return "positive 😊", "The text indicates a positive sentiment."
    elif score < -0.1:
        return "negative 😔", "The text indicates a negative sentiment."
    else:
        return "neutral 😐", "The text indicates a neutral sentiment."

def speak_text(text):
    """Convert the given text to speech using pyttsx3 with livelier settings."""
    engine = pyttsx3.init()
    # Configure lively speech settings
    engine.setProperty("rate", 180)  # Speed up speech rate (default is around 200)
    engine.setProperty("volume", 1.0)  # Set maximum volume
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[0].id)  # Use a preferred voice; change index as needed

    # Speak the text
    engine.say(text)
    engine.runAndWait()


def save_conversation(user_input, response_text, sentiment, recommendations, insights):
    """Save conversation logs to an Excel file."""
    conversation_data = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'user_input': user_input,
        'response_text': response_text,
        'sentiment': sentiment,
        'recommendations': recommendations,
        'insights': insights
    }
    try:
        df = pd.read_excel(log_file)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['timestamp', 'user_input', 'response_text', 'sentiment', 'recommendations', 'insights'])

    new_data = pd.DataFrame([conversation_data])
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_excel(log_file, index=False)

def get_groq_response(user_input):
    """Fetch AI insights and deal recommendations from Groq API with minimal output."""
    groq_url = os.getenv("GROQ_API_URL")
    if not groq_url:
        return "Error: Groq API URL is not configured. Please check the environment settings."
    
    try:
        payload = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "system", "content": "Provide a short and specific response (4–5 lines) with dynamic deal recommendations, insights, and suggestions."},
                {"role": "user", "content": user_input},
            ],
            "max_tokens": 100  # Limit the number of tokens in the response
        }
        response = requests.post(groq_url, json=payload, headers=HEADERS)
        response.raise_for_status()
        api_content = response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response")

        # Ensure the response is concise
        return "\n".join(api_content.split("\n")[:5])  # Return only the first 4–5 lines
    except Exception as e:
        return f"Error fetching insights: {str(e)}"


# ---------- General App Routes ----------

@app_routes.route("/")
def home():
    return render_template("home.html")

@app_routes.route("/sentiment", methods=["GET", "POST"])
def sentiment_analysis():
    if request.method == "POST":
        user_input = request.form.get("user_input")
        if not user_input:
            return render_template("sentiment.html", error="Please enter some text.")
        if not SENTIMENT_API_URL:
            return render_template("sentiment.html", error="SENTIMENT_API_URL is not configured.")

        try:
            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": "Analyze sentiment of the text."},
                    {"role": "user", "content": user_input},
                ]
            }
            response = requests.post(SENTIMENT_API_URL, json=payload, headers=HEADERS)
            response.raise_for_status()
            api_content = response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response")
            sentiment, details = analyze_sentiment_text(api_content)
            return render_template("sentiment.html", sentiment=sentiment, details=details, user_input=user_input)
        except Exception as e:
            return render_template("sentiment.html", error=f"Error: {str(e)}")

    return render_template("sentiment.html")

@app_routes.route("/audio_sentiment", methods=["GET", "POST"])
def audio_sentiment():
    if request.method == "POST":
        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            transcribed_text = recognizer.recognize_google(audio)
            sentiment, details = analyze_sentiment_text(transcribed_text)
            return render_template("sentiment.html", sentiment=sentiment, details=details, user_input=transcribed_text)
        except sr.UnknownValueError:
            return render_template("sentiment.html", error="Could not understand the audio.")
        except Exception as e:
            return render_template("sentiment.html", error=f"Error: {str(e)}")

    return render_template("sentiment.html")

# ---------- Chatbot Routes ----------

@app_routes.route("/chatbot", methods=["GET", "POST"])
def chatbot():
    if request.method == "POST":
        user_message = request.form.get("user_message")
        if not user_message:
            return render_template("chatbot.html", error="Please enter a message.")
        try:
            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": user_message}]
            }
            response = requests.post(CHATBOT_API_URL, json=payload, headers=HEADERS)
            response.raise_for_status()
            assistant_message = response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response")
            return render_template("chatbot.html", user_message=user_message, assistant_message=assistant_message)
        except Exception as e:
            return render_template("chatbot.html", error=f"Error: {str(e)}")

    return render_template("chatbot.html")

# ---------- Conversation Routes ----------

@app_routes.route("/conversation")
def conversation_index():
    return render_template("conversation.html")

@app_routes.route("/start_conversation", methods=["POST"])
def start_conversation():
    speak_text("Hello, audio is listening. Let me know your reviews.")
    return jsonify({"response": "Hello, audio is listening."})

@app_routes.route("/listen", methods=["POST"])
def listen():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Listening for audio...")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

        transcribed_text = recognizer.recognize_google(audio)
        if "stop" in transcribed_text.lower():
            response_text = "Conversation terminated. Goodbye!"
            speak_text(response_text)
            return jsonify({"end": True, "response": response_text, "user_input": transcribed_text})

        # Get sentiment from the transcribed text
        sentiment, sentiment_details = analyze_sentiment_text(transcribed_text)

        # Get AI insights, deal recommendations, and product suggestions from Groq API
        ai_response = get_groq_response(transcribed_text)
        recommendations = f"Suggested products or deal terms: {ai_response}"
        insights = f"Actionable insights: {ai_response}"

        # Save logs
        save_conversation(transcribed_text, ai_response, sentiment, recommendations, insights)

        # Speak AI response
        speak_text(ai_response)
        speak_text("Audio is listening")

        return jsonify({
            "end": False,
            "response": ai_response,
            "sentiment": sentiment,
            "sentiment_details": sentiment_details,
            "recommendations": recommendations,
            "insights": insights,
            "user_input": transcribed_text
        })

    except sr.UnknownValueError:
        error_message = "Could not understand the audio."
        speak_text(error_message)
        speak_text("Audio is listening")
        return jsonify({"end": False, "response": error_message, "user_input": ""})

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        speak_text(error_message)
        speak_text("Audio is listening")
        return jsonify({"end": False, "response": error_message, "user_input": ""})