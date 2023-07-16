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

# This is a global variable that will hold the messages.
msg_list = []

async def cover_play():
    global msg_list
    current_len = 0
    current_msg = 0
    pygame.mixer.init()
    while True:
        print(msg_list)
        # We don't need a while loop here. This function will be called every time a new message is received.
        # len(msg_piece) > 5 or
        # if msg == "&^%&^%&1asdasda&^%*(done)":
        if len(msg_list) != 0 and current_msg == 0:
            current_msg = len(msg_list)-1
        print("123123", len(msg_list), current_msg)
        if len(msg_list) < current_msg+1:
            sleep(1)
            continue
        
        msg = msg_list[current_msg]["msg"]
        state = msg_list[current_msg]["state"]
        data_msg = "".join(msg[current_len:])# Join all messages into one string.
        current_len = len(msg)  
        
        
        print("outspwas", data_msg)
        try:
            communicate = edge_tts.Communicate(data_msg, "zh-CN-XiaoyiNeural")
            
            await communicate.save("./AI_to_speak/outputaudio/out.mp3")
            # audio_segment = AudioSegment.from_file(temp_filename, format="mp3")
            # AudioSegment.from_file(temp_filename).export(temp_filename, format="wav")
            audio = AudioSegment.from_mp3("./AI_to_speak/outputaudio/out.mp3")
            audio.export("./AI_to_speak/outputaudio/out.wav", format="wav")

            pygame.mixer.init()  # Initialize the mixer module
            sound = pygame.mixer.Sound("./AI_to_speak/outputaudio/out.wav")
            sound.play()
        except:
            pass
        while pygame.mixer.get_busy():
            sleep(0.1)

        # Cleanup
        
        if (state == "done"):
            # pygame.mixer.quit()
            current_msg += 1
            current_len = 0
            print("current_msg add one", current_msg)
        elif (state == "inginging"):
            current_msg = current_msg
            continue
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
