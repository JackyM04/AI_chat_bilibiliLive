import json


from bilibili_client import BiliClient

with open('./config.json', 'r') as f:
    data = json.load(f)
 
cli = BiliClient(
    idCode = data["idCode"],
    appId = data["appId"],
    key = data["key"],
    secret = data["secret"],
    host="https://live-open.biliapi.com")
cli.run()