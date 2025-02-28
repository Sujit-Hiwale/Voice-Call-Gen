import pyttsx3

engine = pyttsx3.init()
text = input("Enter your prompt: ")
engine.say(text)
engine.runAndWait()