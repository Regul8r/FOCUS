import os
import anthropic
from elevenlabs.client import ElevenLabs
from elevenlabs import play
from dotenv import load_dotenv
import pygame
import io

load_dotenv()

anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
eleven_client = ElevenLabs(api_key=os.getenv('ELEVENLABS_API_KEY'))

def generate_summary(accounts):
    account_info = "\n".join([
        f"{a['name']}: ${a['balance']:.2f} (goal: ${a['goal']:.2f}, status: {a['health']})"
        for a in accounts
    ])
    
    message = anthropic_client.messages.create(
        model="claude-opus-4-20250514",
        max_tokens=200,
        messages=[{
            "role": "user",
            "content": f"""You are FOCUS, a friendly financial awareness assistant. 
            Give a warm, encouraging 2-3 sentence daily summary for this user's accounts.
            Sound like a supportive friend, not a bank. Be specific about the numbers.
            
            Accounts:
            {account_info}"""
        }]
    )
    return message.content[0].text

def speak_summary(accounts):
    summary = generate_summary(accounts)
    print(f"FOCUS says: {summary}")
    
    audio = eleven_client.text_to_speech.convert(
        text=summary,
        voice_id="EXAVITQu4vr4xnSDxMaL",
        model_id ="eleven_turbo_v2_5"
    )
    audio_bytes = b"".join(audio)
    pygame.mixer.init()
    pygame.mixer.music.load(io.BytesIO(audio_bytes))
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    return summary

if __name__ == "__main__":
    import json
    with open('focus_data.json') as f:
        accounts = json.load(f)
    speak_summary(accounts)
