import speech_recognition as sr
import google.generativeai as genai
import requests
import os
import time
import pygame
import streamlit as st
from gtts import gTTS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# SERPAPI Key
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

# Load Gemini model
model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")

def gemini_search(query):
    """Search using Gemini AI"""
    response = model.generate_content(query)
    return response.text

def google_search(query):
    """Search using Google Search API"""
    params = {
        "q": query,
        "api_key": SERPAPI_API_KEY,
        "engine": "google",
    }
    try:
        response = requests.get("https://serpapi.com/search", params=params)
        data = response.json()
        if "organic_results" in data and len(data["organic_results"]) > 0:
            return data["organic_results"][0].get("snippet", "No snippet found.")
        else:
            return "No real-time results found."
    except Exception as e:
        print(f"Google Search Error: {e}")
        return "Failed to fetch real-time information."

def listen():
    """Listen to user's voice input"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        with st.spinner('🎤 Listening...'):
            audio = recognizer.listen(source)
    try:
        query = recognizer.recognize_google(audio)
        return query
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        return ""

def speak(text):
    """Convert text to speech and play it"""
    try:
        # Create a temporary file with timestamp to avoid conflicts
        timestamp = int(time.time())
        temp_file = f"temp_speech_{timestamp}.mp3"
        
        # Generate speech
        tts = gTTS(text=text, lang='en')
        tts.save(temp_file)
        
        # Play the audio
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        
        # Wait for playback to complete
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        
        # Add small delay to ensure complete playback
        time.sleep(0.5)
        
    except Exception as e:
        print(f"Speech error: {e}")
    finally:
        # Always try to clean up the temporary file
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except:
            pass
            
    # Set session state to indicate speech is complete
    if 'speech_completed' in st.session_state:
        st.session_state.speech_completed = False 