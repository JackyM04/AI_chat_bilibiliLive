from fastapi import FastAPI, UploadFile, Form, WebSocket
from fastapi import BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import edge_tts
import pygame
import asyncio
import io
import threading
from pydub import AudioSegment
from playsound import playsound
import tempfile
from time import sleep
import json
from pydantic import BaseModel


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    pygame.mixer.init()

@app.post("/API/AI_to_speak")
async def hendlemessage(
    msg: str = Form(...),
    message_system: str = Form(...),
    ):
    
    
    data_msg = msg
    print("speaking:", data_msg, end="", flush=True)
    try:
        communicate = edge_tts.Communicate(data_msg, "zh-CN-XiaoyiNeural")
        
        await communicate.save(f"./AI_to_speak/outputaudio/out.mp3")
        # audio_segment = AudioSegment.from_file(temp_filename, format="mp3")
        # AudioSegment.from_file(temp_filename).export(temp_filename, format="wav")
        audio = AudioSegment.from_mp3(f"./AI_to_speak/outputaudio/out.mp3")
        audio.export(f"./AI_to_speak/outputaudio/out.wav", format="wav")

        pygame.mixer.init()  # Initialize the mixer module
        sound = pygame.mixer.Sound(f"./AI_to_speak/outputaudio/out.wav")
        sound.play()
    except:
        pass
    while pygame.mixer.get_busy():
        sleep(0.1)
    reply = {
        "message_system": "done"
    }
    return json.dumps(reply)




#uvicorn AI_to_speak.main_speak:app --port 10082 --reload
