import streamlit as st
import speech_recognition as sr
import google.generativeai as genai
import requests
import os
import sys
import subprocess
import webbrowser
import threading
import time
import pygame
from gtts import gTTS
from dotenv import load_dotenv
import re
import platform
import pyaudio

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key="AIzaSyCaQA83xmWeQHyuthRF-WYv7addpWB9Z0U")

# SERPAPI Key
SERPAPI_API_KEY ="15312b3846f7eab5856197af0ea4b08787a03d38d968afedad278cd1cdc2c006"

# Load Gemini model
model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")

# Detect OS
SYSTEM_OS = platform.system()  # 'Windows', 'Darwin' (Mac), or 'Linux'

# Initialize pygame mixer for audio playback
try:
    pygame.mixer.quit()  # First quit any existing mixer
    pygame.mixer.init()
except Exception as e:
    print(f"Pygame mixer initialization error: {e}")

# Functions
def gemini_search(query):
    response = model.generate_content(query)
    return response.text

def google_search(query):
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

# Application Control Functions
def open_application(app_name):
    """Opens an application based on the detected operating system"""
    app_name = app_name.lower()
    result = f"Attempting to open {app_name}..."
    
    try:
        if SYSTEM_OS == 'Windows':
            # Windows application mapping
            app_map = {
                'notepad': 'notepad.exe',
                'calculator': 'calc.exe',
                'word': 'winword.exe',
                'excel': 'excel.exe',
                'chrome': 'chrome.exe',
                'firefox': 'firefox.exe',
                'edge': 'msedge.exe',
                'file explorer': 'explorer.exe',
                'paint': 'mspaint.exe',
                'cmd': 'cmd.exe',
                'powershell': 'powershell.exe',
                'task manager': 'taskmgr.exe',
                'control panel': 'control.exe',
                'spotify': 'spotify.exe',
                'vlc': 'vlc.exe'
            }
            
            # Check if app is in our map
            for key in app_map:
                if key in app_name:
                    subprocess.Popen(app_map[key])
                    return f"Opened {key}"
            
            # If not in map, try to run the command directly
            subprocess.Popen(app_name)
            return result
            
        elif SYSTEM_OS == 'Darwin':  # macOS
            # Mac application mapping
            app_map = {
                'safari': 'Safari',
                'chrome': 'Google Chrome',
                'firefox': 'Firefox',
                'terminal': 'Terminal',
                'finder': 'Finder',
                'calculator': 'Calculator',
                'notes': 'Notes',
                'word': 'Microsoft Word',
                'excel': 'Microsoft Excel',
                'powerpoint': 'Microsoft PowerPoint',
                'music': 'Music',
                'photos': 'Photos',
                'system preferences': 'System Preferences',
                'spotlight': 'Spotlight',
                'messages': 'Messages',
                'mail': 'Mail'
            }
            
            # Check if app is in our map
            for key in app_map:
                if key in app_name:
                    os.system(f"open -a '{app_map[key]}'")
                    return f"Opened {app_map[key]}"
            
            # Try to open it directly if not in map
            os.system(f"open -a '{app_name}'")
            return result
            
        elif SYSTEM_OS == 'Linux':
            # Linux application mapping
            app_map = {
                'firefox': 'firefox',
                'chrome': 'google-chrome',
                'terminal': 'gnome-terminal',
                'calculator': 'gnome-calculator',
                'gedit': 'gedit',
                'files': 'nautilus',
                'spotify': 'spotify',
                'vlc': 'vlc',
                'libreoffice': 'libreoffice',
                'settings': 'gnome-control-center',
                'thunderbird': 'thunderbird'
            }
            
            # Check if app is in our map
            for key in app_map:
                if key in app_name:
                    subprocess.Popen([app_map[key]])
                    return f"Opened {key}"
            
            # Try to open it directly if not in map
            subprocess.Popen([app_name])
            return result
            
    except Exception as e:
        return f"Failed to open {app_name}: {str(e)}"

def open_website(url):
    """Opens a website in the default browser"""
    try:
        # Add http if not present
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        webbrowser.open(url)
        return f"Opened {url}"
    except Exception as e:
        return f"Failed to open {url}: {str(e)}"

def execute_system_command(command):
    """Executes a system command with safety restrictions"""
    # List of dangerous commands to avoid
    dangerous_commands = [
        'rm -rf', 'format', 'deltree', 'shutdown', 'reboot', 'halt',
        'del /f', 'del /q', ':(){:|:&};:', 'mkfs', 'dd if=/dev/zero',
        '> /dev/sda', 'wipe', '> /dev/null', 'attrib', '> nul'
    ]
    
    # Check if command contains any dangerous patterns
    if any(dangerous in command.lower() for dangerous in dangerous_commands):
        return "Sorry, I cannot execute potentially harmful system commands."
    
    try:
        # Execute command and capture output
        if SYSTEM_OS == 'Windows':
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            process = subprocess.Popen(['/bin/bash', '-c', command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
        output, error = process.communicate(timeout=5)
        
        if error:
            return f"Command executed with error: {error.decode('utf-8')}"
        return f"Command executed: {output.decode('utf-8')}"
    except subprocess.TimeoutExpired:
        return "Command timed out after 5 seconds."
    except Exception as e:
        return f"Failed to execute command: {str(e)}"

def search_files(query):
    """Search for files on the system"""
    try:
        location = os.path.expanduser("~")  # Default to home directory
        pattern = "*"
        
        # Extract location if specified
        location_match = re.search(r'in\s+(.+?)(\s+for|\s*$)', query)
        if location_match:
            location = location_match.group(1)
            location = os.path.expanduser(location.strip())
        
        # Extract file pattern
        pattern_match = re.search(r'for\s+(.+?)(\s+in|\s*$)', query)
        if pattern_match:
            pattern = pattern_match.group(1).strip()
            
        # Add wildcards for better matches
        if not '*' in pattern:
            pattern = f"*{pattern}*"
            
        # Execute the search command based on OS
        if SYSTEM_OS == 'Windows':
            command = f'dir /s /b "{os.path.join(location, pattern)}"'
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:  # Linux or Mac
            command = f'find "{location}" -name "{pattern}" -type f | head -n 10'
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
        output, error = process.communicate(timeout=10)
        
        # Process results
        if output:
            files = output.decode('utf-8').strip().split('\n')
            if len(files) > 10:
                return f"Found {len(files)} files. Here are the first 10:\n" + '\n'.join(files[:10])
            elif len(files) > 0:
                return f"Found {len(files)} files:\n" + '\n'.join(files)
        
        return "No files found matching your criteria."
    except Exception as e:
        return f"Error searching for files: {str(e)}"

def process_command(query):
    """Process the user's command to determine if it's a system action"""
    query = query.lower()
    
    # Check for application opening commands
    if re.search(r'open\s+(.+?)\s*(application|app)?', query):
        app_name = re.search(r'open\s+(.+?)(\s+application|\s+app|\s*$)', query).group(1).strip()
        
        # Check if it's a website
        if '.' in app_name and any(tld in app_name for tld in ['.com', '.org', '.net', '.edu', '.gov', '.io']):
            return open_website(app_name)
        else:
            return open_application(app_name)
    
    # Check for website opening commands
    elif re.search(r'(open|go\s+to|navigate\s+to|visit)\s+(website|site|webpage)?\s*(.+\.(com|org|net|edu|gov|io))', query):
        url = re.search(r'(open|go\s+to|navigate\s+to|visit)\s+(website|site|webpage)?\s*(.+\.(com|org|net|edu|gov|io))', query).group(3).strip()
        return open_website(url)
    
    # Check for system commands
    elif re.search(r'(execute|run)\s+command\s+(.+)', query):
        cmd = re.search(r'(execute|run)\s+command\s+(.+)', query).group(2).strip()
        return execute_system_command(cmd)
    
    # Check for file search
    elif re.search(r'(search|find|locate)\s+(file|files|document|documents)', query):
        return search_files(query)
    
    # If no system action matches, return None to use AI response
    return None

# Custom CSS for better UI
def local_css():
    try:
        css_text = open(".streamlit/style.css").read()
        st.markdown(f'<style>{css_text}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        # Default CSS if file not found
        st.markdown("""
        <style>
        .chat-container {
            padding: 10px;
        }
        .chat-bubble {
            padding: 10px;
            border-radius: 15px;
            margin: 5px 0;
            display: inline-block;
            max-width: 80%;
        }
        .user {
            background-color: #e6f7ff;
            float: right;
            clear: both;
        }
        .assistant {
            background-color: #f0f0f0;
            float: left;
            clear: both;
        }
        </style>
        """, unsafe_allow_html=True)

# Streamlit UI
st.set_page_config(page_title="Advanced Voice Assistant", page_icon="🎙️", layout="centered")
local_css()

# Add a callback when the session is reset
if st.session_state.get('_is_new_session', True):
    st.session_state._is_new_session = False
    # Ensure pygame mixer is properly initialized on session restart
    if pygame.mixer.get_init() is None:
        pygame.mixer.init()

st.title("🎙️ Advanced Voice Assistant")
st.markdown("Talk or Type your query and chat with your assistant! Now with application control!")

# Display capability information
with st.expander("What can this assistant do?"):
    st.markdown("""
    ### Voice Commands
    - **Open applications**: "Open Notepad", "Open Chrome", "Open Calculator"
    - **Visit websites**: "Open google.com", "Go to youtube.com"
    - **Search files**: "Search for documents in Downloads", "Find excel files"
    - **Execute commands**: "Execute command dir" (use with caution)
    
    ### Other Capabilities
    - Answer questions using AI
    - Get real-time information for keywords like "today", "latest", "news", etc.
    - Speak responses out loud
    """)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
    
# Track if we need to speak the response
if 'should_speak' not in st.session_state:
    st.session_state.should_speak = False
    
# Track speaking status
if 'speech_completed' not in st.session_state:
    st.session_state.speech_completed = False

col1, col2 = st.columns(2)

with col1:
    mic = st.button("🎤 Speak")
with col2:
    st.text_input("Or Type your query:", key="typed_query")

# Handling Input
query = ""
if mic:
    query = listen()
    if query:
        st.session_state.messages.append(("user", query))
if st.session_state.typed_query:
    query = st.session_state.typed_query
    st.session_state.messages.append(("user", query))
    st.session_state.typed_query = ""

# Generate Response
if query:
    # Indicate that speech should happen after this response
    st.session_state.should_speak = True
    
    # First check if it's a system command
    system_response = process_command(query)
    
    if system_response:
        # It was a system command, use the result
        answer = system_response
    else:
        # Not a system command, use AI or search
        keywords = ["today", "latest", "news", "price", "time", "live", "score", "weather", "update"]
        if any(word in query.lower() for word in keywords):
            answer = google_search(query)
        else:
            answer = gemini_search(query)

    # Add to message history
    st.session_state.messages.append(("assistant", answer))
    
    # Create a speech status indicator
    speech_status = st.empty()
    speech_status.info("🔊 Speaking...")
    
    # Create and start the thread for speech
    speech_thread = threading.Thread(target=speak, args=(answer,))
    speech_thread.daemon = True  # Make thread terminate when main program exits
    speech_thread.start()
    
    # Trigger a rerun after a short delay for better UI feedback
    st.session_state.speech_completed = True
    time.sleep(0.5)  # Small delay to ensure speech starts
    speech_status.empty()  # Clear the status after speech starts

# Show Conversation
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for sender, msg in st.session_state.messages:
    if sender == "user":
        st.markdown(f'<div class="chat-bubble user">{msg}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bubble assistant">{msg}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("------------------------------------------------------------")
st.caption("Made by Daksh Vikma + Gemini AI.")
