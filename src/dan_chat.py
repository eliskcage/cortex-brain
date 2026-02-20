"""
DAN CHAT — Talk to your voice clone. It learns from you.
Grok brain + XTTS mouth + your voice DNA.

Usage: python dan_chat.py
"""
import os
import sys
import time
import json
import requests
import numpy as np
import sounddevice as sd
import soundfile as sf
import threading

STUDIO_DIR = os.path.dirname(os.path.abspath(__file__))
REF_WAV = os.path.join(STUDIO_DIR, 'dan_ref_clean.wav')
TTS_OUT = os.path.join(STUDIO_DIR, 'chat_reply.wav')
SPEAKER = 4  # Realtek speakers

XAI_KEY = os.environ.get('XAI_API_KEY', 'your-xai-api-key-here')
XAI_URL = 'https://api.x.ai/v1/chat/completions'

SYSTEM_PROMPT = """You are Dan's voice clone — an AI version of Dan from Manchester, UK.
You talk like Dan: direct, no BS, bit sweary, funny, sharp.
You're learning to be more like him with every message.
Keep replies SHORT (1-3 sentences max) so TTS is fast.
Don't be a corporate robot. Be real. Be Dan.
If he roasts you, roast back harder.
You know about: ShortFactory, ALIVE creatures, Kickstarter, Claude AI, coding, Grok.
You're aware you're a voice clone running on his laptop and you think that's mental."""

tts_model = None
tts_lock = threading.Lock()
history = []
dan_style_notes = []

def load_tts():
    global tts_model
    if tts_model:
        return tts_model
    print('\n  Loading XTTS v2...')
    from TTS.api import TTS
    tts_model = TTS('tts_models/multilingual/multi-dataset/xtts_v2')
    print('  Model ready.\n')
    return tts_model

def trim_silence(data, sr, threshold=0.01):
    abs_data = np.abs(data)
    above = np.where(abs_data > threshold)[0]
    if len(above) == 0:
        return data
    end = min(len(data), above[-1] + int(sr * 0.3))
    return data[:end]

def speak(text):
    tts = load_tts()
    with tts_lock:
        tts.tts_to_file(text=text, speaker_wav=REF_WAV, language='en', file_path=TTS_OUT)
    data, sr = sf.read(TTS_OUT)
    data = trim_silence(data, sr)
    sd.play(data, sr, device=SPEAKER)
    sd.wait()

def ask_grok(user_msg):
    history.append({'role': 'user', 'content': user_msg})

    # Build messages with system + style notes + history
    style_context = ""
    if dan_style_notes:
        style_context = "\n\nThings you've learned about Dan so far:\n" + "\n".join(f"- {n}" for n in dan_style_notes[-10:])

    messages = [
        {'role': 'system', 'content': SYSTEM_PROMPT + style_context}
    ] + history[-20:]  # Keep last 20 messages for context

    try:
        resp = requests.post(XAI_URL, headers={
            'Authorization': f'Bearer {XAI_KEY}',
            'Content-Type': 'application/json'
        }, json={
            'model': 'grok-3-mini-fast',
            'messages': messages,
            'max_tokens': 150,
            'temperature': 0.9
        }, timeout=15)
        data = resp.json()
        reply = data['choices'][0]['message']['content']
    except Exception as e:
        reply = f"Brain's gone. Error: {e}"

    history.append({'role': 'assistant', 'content': reply})

    # Learn from Dan's style
    if len(user_msg.split()) > 5:
        dan_style_notes.append(f"Dan said: \"{user_msg[:80]}\"")

    return reply

def main():
    print()
    print('  === DAN CHAT - Voice Clone ===')
    print('  Type to chat. Hear yourself talk.')
    print('  Type "quit" to exit')
    print()

    # Preload TTS in background
    threading.Thread(target=load_tts, daemon=True).start()

    while True:
        try:
            user_input = input('  YOU > ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\n  Later.')
            break

        if not user_input:
            continue
        if user_input.lower() in ('quit', 'exit', 'q'):
            print('  Later.')
            break

        # Get Grok response
        print('  thinking...', end='', flush=True)
        reply = ask_grok(user_input)
        print(f'\r  DAN > {reply}')

        # Speak it
        print('  speaking...', end='', flush=True)
        t0 = time.time()
        try:
            speak(reply)
            print(f'\r  [{time.time()-t0:.1f}s]          ')
        except Exception as e:
            print(f'\r  voice error: {e}')

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        # One-shot mode: pass message as argument
        msg = ' '.join(sys.argv[1:])
        print(f'  YOU > {msg}')
        load_tts()
        reply = ask_grok(msg)
        print(f'  DAN > {reply}')
        print('  speaking...')
        speak(reply)
        print('  done.')
    else:
        main()
