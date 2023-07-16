import requests
from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from random import randint
import json
from time import sleep
import threading
import asyncio
import websockets
import copy

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

with open('./config.json', 'r', encoding='utf-8') as f:
    config_data = json.load(f)

msg_wait_list = []
msg_processed_list = {}
async def recive_message():
    pass

async def AI_language():
    global msg_wait_list, msg_processed_list
    uri = config_data["URL_AI_language"]

    while True:
        if len(msg_wait_list) == 0 or len(msg_processed_list) != 0:
            print("\nAI_languag: waiting", end="", flush=True)
            sleep(1)
            continue

        async with websockets.connect(uri) as websocket:
            msg_list = msg_wait_list.copy()
            msg_wait_list = []
            msg = msg_list[randint(0, len(msg_list)-1)]
            send_msg = {
                "msg": msg,
                "message_system": "start"
            }
            await websocket.send(json.dumps(send_msg))

            while websocket.close_code is None:
                response = await websocket.recv()
                response = json.loads(response)
                msg_processed_list[msg] = {
                    "processed_msg": response["msg"],
                    "state": response["state"]
                }

                if msg_processed_list.get(msg) == None or msg_processed_list.get(msg)["state"] == "done":
                    break
                
async def send_to_speak():
    global msg_wait_list, msg_processed_list
    uri = config_data["URL_ai_to_speak"]
    current_length = 0

    while True:
        if len(msg_processed_list) == 0:
                print("\nsend_to_speak: waiting", end="", flush=True)
                sleep(1)
                continue
        
        key = next(iter(msg_processed_list))
        message_dict = copy.deepcopy(msg_processed_list[key])
        if message_dict["state"] == "done":
            msg_text = message_dict["processed_msg"]
            msg = msg_text[current_length:]
            current_length = 0
        elif current_length == 0:
            msg_text = message_dict["processed_msg"]
            msg = key+ "    " + msg_text[current_length:]
            current_length = len(msg_text)
        else:
            msg_text = message_dict["processed_msg"]
            msg = msg_text[current_length:]
            current_length = len(msg_text)

        msg_data = [
            ("msg", msg),
            ("message_system", "start")
        ]
        response = requests.post(uri, msg_data)
        data = response.json()
        data = json.loads(data)
        if data["message_system"] == "done":
            if message_dict["state"] == "done":
                del msg_processed_list[key]
            continue

def run_loop(funtion):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(funtion())
    loop.close()

@app.on_event("startup")
async def startup_event():
    global msg_wait_list, msg_processed_list
    msg_wait_list = []
    msg_processed_list = {}
    thread1 = threading.Thread(target=run_loop, args=(AI_language,))
    thread2 = threading.Thread(target=run_loop, args=(send_to_speak,))
    thread1.start()
    thread2.start()

@app.post("/API/text_process")
async def hendlemessage(
    uname: str = Form(...),
    fans_medal_wearing_status: str = Form(...),
    guard_level: str = Form(...),
    msg: str = Form(...)
    ):
    print("333333")
    msg_wait_list.append(msg)
    print("123123123", msg_wait_list)
    return None

#uvicorn text_to_AI.main_AI:app --port 10081 --reload --log-level debug