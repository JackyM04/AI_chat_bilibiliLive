from fastapi import FastAPI, UploadFile, Form
from fastapi import BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import edge_tts
import pygame
import asyncio
import io
from pydub import AudioSegment
from playsound import playsound
import tempfile

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# This is a global variable that will hold the messages.
msg_piece = []
last_processed_index = 0

async def cover_play():
    global msg_piece, last_processed_index
    current_len = 0
    # We don't need a while loop here. This function will be called every time a new message is received.
    # len(msg_piece) > 5 or
    # if msg == "&^%&^%&1asdasda&^%*(done)":
    data_msg = "".join(msg_piece[last_processed_index:])# Join all messages into one string.
    last_processed_index = len(msg_piece)  
    
    
    print("123123", data_msg)
    communicate = edge_tts.Communicate(data_msg, "zh-CN-XiaoyiNeural")
    
    await communicate.save("./AI_to_speak/outputaudio/out.mp3")
    # audio_segment = AudioSegment.from_file(temp_filename, format="mp3")
    # AudioSegment.from_file(temp_filename).export(temp_filename, format="wav")
    audio = AudioSegment.from_mp3("./AI_to_speak/outputaudio/out.mp3")
    audio.export("./AI_to_speak/outputaudio/out.wav", format="wav")

    pygame.mixer.init()  # Initialize the mixer module
    sound = pygame.mixer.Sound("./AI_to_speak/outputaudio/out.wav")
    sound.play()
    while pygame.mixer.get_busy():
        await asyncio.sleep(0.1)

    # Cleanup
    pygame.mixer.quit()


@app.post("/API/AI_to_speak")
async def hendlemessage(
    background_tasks: BackgroundTasks,
    msg: str = Form(...),
    state: str = Form(...)
):
    print(msg, state)
    global msg_piece
    
    print('ready to cover')
    msg_piece = list(msg)  # Here we don't need "await", because append() is not an asynchronous operation.
    if '，' in msg or '。' in msg or state == "done":
        print('，' in msg or '。' in msg)
        print('ready to cover')
        background_tasks.add_task(cover_play)

# if __name__ == "__main__":
#     for i in range(6):
#         msg = input(f"{i+1}::::")
#         msg_piece.append(msg)
#         asyncio.run(cover_play(msg))

#uvicorn AI_to_speak.main_speak:app --port 10082 --reload
