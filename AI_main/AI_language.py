from transformers import AutoTokenizer, AutoModel
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import json


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
msg_wait_list = []

with open('./config.json', 'r', encoding='utf-8') as f:
    config_data = json.load(f)
tokenizer = AutoTokenizer.from_pretrained(config_data["model_path"], trust_remote_code=True)
num_GPU = config_data["number_GPU"]
if num_GPU == 1:
    model = AutoModel.from_pretrained(config_data["model_path"], trust_remote_code=True).cuda()
elif num_GPU == 0:
    pass
else:
    from AI_main.utils import load_model_on_gpus
    model = load_model_on_gpus(config_data["model_path"], num_gpus=int(num_GPU))
model = model.eval()

stop_stream = False
history = []
past_key_values = None
system_promote = (config_data["system_promote"]["prompt"], config_data["system_promote"]["answer"])


@app.websocket("/API/AI_language")
async def hendlemessage(
    websocket: WebSocket 
    ):
    global history
    global past_key_values, stop_stream, system_promote
    await websocket.accept()
    while True:
        history.append(system_promote)
        current_length = 0
        data = await websocket.receive_text()
        data = json.loads(data)
        if "message_system" in data and data == "STOP":  # 如果客户端发送了"STOP"消息，停止发送并关闭连接
            await websocket.close()
            return

        for response, current_history in model.stream_chat(tokenizer, data["msg"], history=history,
                                                                past_key_values=None,
                                                                max_length=10000,
                                                                top_p=0.7,
                                                                temperature=0.7,
                                                                return_past_key_values=False):
            if stop_stream:
                stop_stream = False
                print("\n")
            else:
                print(response[current_length:], end="", flush=True)
                current_length = len(response)
                replay = {
                    "msg": response,
                    "state": "working"
                }
                await websocket.send_text(json.dumps(replay))

        history = current_history
        # past_key_values = current_past_key_values
        current_length = 0
        replay = {
                "msg": response,
                "state": "done"
            }
        await websocket.send_text(json.dumps(replay))
        

#uvicorn text_to_AI.main_AI:app --port 10083 --reload