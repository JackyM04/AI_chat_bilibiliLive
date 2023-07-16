import json
import requests
class handmessages:
    def __init__(self) -> None:
        with open('./config.json', 'r') as f:
            self.data = json.load(f)
    async def sendmessage(self, message_dict: str):
        print(message_dict)
        try:
            message_dict = json.loads(message_dict)
        except:
            return
        print("123123123",type(message_dict))
        #初步筛选条件
        if message_dict["cmd"] != "LIVE_OPEN_PLATFORM_DM":
            return
        fans_data = message_dict["data"]
        if fans_data["dm_type"] != 0:
            return
        if (self.data["fans_medal_wearing_only_mode"] 
            and fans_data["fans_medal_wearing_status"] == False):
            return
        if (self.data["guard_only_mode"] and fans_data["guard_level"] == 0):
            return
        
        fans_send_data = [
            ("uname", fans_data["uname"]),
            ("fans_medal_wearing_status", fans_data["fans_medal_wearing_status"]),
            ("guard_level", fans_data["guard_level"]),
            ("msg", fans_data["msg"])
        ]
         
        response = requests.post(self.data['URL_text_process'], fans_send_data)
        print("send_done")


        


        
