import os
import pyttsx3
import speech_recognition as sr
import google.generativeai as genai
import google.api_core.exceptions
import re

engine = pyttsx3.init()
engine.setProperty('rate', 150)

recognizer = sr.Recognizer()
mic = sr.Microphone()

os.environ["GRPC_ENABLE_FORK_SUPPORT"] = "0"
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GRPC_POLL_STRATEGY"] = "poll"

API_KEY = "API KEY"  # Replace with your actual API key
genai.configure(api_key=API_KEY)

def clean_text(text):
    """Remove unnecessary symbols and bracketed content from AI response."""
    text = re.sub(r'\*.*?\*', '', text)
    text = re.sub(r'[*]', '', text)
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\(.*?\)', '', text)
    return text.strip()

def chat_with_character(character_name, latest_message, conversation_history):
    """Generate a real-time response from the AI character based on only the latest user message."""
    model = genai.GenerativeModel("GEMINI MODEL") #Replace with the Gemini Model you want to use

    prompt = (
        f"You are {character_name}, talking on a phone call. Reply naturally and keep it short. "
        f"Here is what the user just said:\nUser: {latest_message}\n{character_name}:"
    )

    try:
        response = model.generate_content(prompt, generation_config={"max_output_tokens": 50})
        ai_text = clean_text(response.text) if response.text else "I'm not sure how to respond."
        return ai_text
    except google.api_core.exceptions.GoogleAPIError as e:
        print("API error:", e)  # Debugging log
        return "I didn't catch that. Can you repeat?"

def listen():
    """Capture and process audio input with fallback to text if no audio is detected."""
    with mic as source:
        print("\n🎤 Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            text = recognizer.recognize_google(audio).strip()
            if text:
                print(f"You (audio): {text}")
                return text.lower()
        except sr.WaitTimeoutError:
            print("⏳ No speech detected.")
        except sr.UnknownValueError:
            print("🤷 Could not understand audio.")
        except sr.RequestError as e:
            print(f"⚠️ Speech recognition error: {e}")

    return None

character_name = input("Enter the character you want to speak with: ")

conversation_history = []
print(f"\n📞 Calling {character_name}... (Say 'exit' or 'quit' to hang up)\n")

while True:
    user_message = listen()

    if user_message is None:
        user_message = input("No audio detected. Please type your message: ").strip().lower()
        if not user_message:
            continue

    if user_message in ["exit", "quit"]:
        print(f"{character_name}: Alright, talk later!")
        engine.say("Alright, talk later!")
        engine.runAndWait()
        break

    ai_response = chat_with_character(character_name, user_message, conversation_history)
    conversation_history.append({"user": user_message, "ai": ai_response})
    
    print(f"{character_name}: {ai_response}\n")
    engine.say(ai_response)
    engine.runAndWait()
