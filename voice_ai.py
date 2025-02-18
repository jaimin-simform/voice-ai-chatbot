import openai
import random
from scipy.io.wavfile import write
import sounddevice as sd
import pyttsx3
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Set OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

# List of adjectives and nouns to generate random names for voice recordings
adjectives = ["beautiful", "sad", "mystical", "serene", "whispering", "gentle", "melancholic"]
nouns = ["sea", "love", "dreams", "song", "rain", "sunrise", "silence", "echo"]

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Set the speech speed rate
engine.setProperty('rate', 185)

def change_voice(engine, language, gender='VoiceGenderFemale'):
    """
    Change the voice of the text-to-speech engine.
    Args:
        engine: pyttsx3 engine instance.
        language: Language code (e.g., 'en_US').
        gender: Voice gender ('VoiceGenderFemale' or 'VoiceGenderMale').
    Returns:
        True if successful, otherwise prints an error message.
    """
    try:
        for voice in engine.getProperty('voices'):
            if language in voice.languages and gender == voice.gender:
                engine.setProperty('voice', voice.id)
                return True
        raise RuntimeError(f"Language '{language}' for gender '{gender}' not found")
    except:
        print("Language not found")

# Set the default voice to female English
change_voice(engine, "en_US", "VoiceGenderFemale")

def generate_random_name():
    """
    Generate a random name using predefined adjectives and nouns.
    Returns:
        A string representing the generated name.
    """
    adjective = random.choice(adjectives)
    noun = random.choice(nouns)
    return f"{adjective} {noun}"

def new_record_audio():
    """
    Record an audio sample and save it as a WAV file.
    Returns:
        The path to the saved WAV file.
    """
    print("Recording... Press 's' to stop.")
    fs = 48000  # Sample rate
    seconds = 6  # Duration of the recording
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, blocking=True)
    sd.wait()  # Wait until the recording is finished
    
    # Generate a unique name for the audio file
    audio_name = generate_random_name()
    audio_path = f'./voices/{audio_name}.wav'
    
    # Save the recording as a WAV file
    write(audio_path, fs, myrecording)
    print("Recording stopped.")
    return audio_path

def speech_to_text(audio_path):
    """
    Convert speech from an audio file to text using OpenAI's Whisper model.
    Args:
        audio_path: Path to the WAV file.
    Returns:
        The transcribed text from the audio.
    """
    print("Entered transcribe:", audio_path)
    with open(audio_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    print(transcript)
    return transcript['text']

def text_to_speech(response):
    """
    Convert text to speech and play the audio.
    Args:
        response: The text to be converted into speech.
    """
    engine.say(response)
    engine.runAndWait()

def openai_chat_send(transcript):
    """
    Send the transcribed text to OpenAI's ChatGPT and get a response.
    Args:
        transcript: User's input text.
    Returns:
        The AI-generated response.
    """
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": transcript}
    ]
    print("Transcript:")
    print(transcript)
    
    # Make API call to OpenAI
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return completion.choices[0].message["content"]

def main():
    """
    Main function to continuously record audio, transcribe, and get AI-generated responses.
    """
    while True:
        print("Press 's' to stop recording and transcribe the audio.")
        
        # Record the user's voice
        recorded_audio_path = new_record_audio()
        print("Recording stopped. Transcribing audio...")
        print("Recorded audio saved to:", recorded_audio_path)
        print("----end---")
        
        # Convert speech to text
        transcript = speech_to_text(recorded_audio_path)
        
        # Send transcribed text to OpenAI ChatGPT
        response = openai_chat_send(transcript)
        
        # Print the AI-generated response
        print("Assistant:", response)
        
        # Convert the response to speech
        text_to_speech(response)

if __name__ == "__main__":
    main()
