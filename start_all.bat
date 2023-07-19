cd C:\Users\32607\Desktop\AI_stream\AI_chat_bilibiliLive
call conda activate AI_Chat

start python -m http.server

start uvicorn AI_main.AI_language:app --port 10083 --reload

start python .\bilibili_To_Text\main_gettext.py

start uvicorn AI_to_speak.main_speak:app --port 10082 --reload

start uvicorn AI_main.main_AI:app --port 10081 --reload
pause
