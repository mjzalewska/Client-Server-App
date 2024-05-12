import json


class Message:
    def __init__(self, msg_text):
        self.msg_text = msg_text
        self.header = {"encoding": "utf-8",
                       "length": len(self.msg_text)
                       }

    def read(self):
        message = json.loads(self.msg_text).decode(self.header["encoding"])
        return message

    def write(self):
        message = json.dumps(self.msg_text)
        return message
