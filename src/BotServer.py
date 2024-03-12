import json
import apiai
from flask import Flask, request, abort
from database import Database
# Line API
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError

''' LINE Developers get api
Messaging API → Channel access token
Basic settings → Channel secret)
'''
line_bot_api = LineBotApi("Channel access token")
handler = WebhookHandler("Channel secret")
# dialogflow CLIENT_ACCESS_TOKEN
# https://dialogflow.cloud.google.com/#/agent/chat-rujcse/intents
CLIENT_ACCESS_TOKEN = 'CLIENT_ACCESS_TOKEN'
DB = Database(DB="chatbot", user="root", password="0000")
app = Flask(__name__)

# Line connect
@app.route("/", methods=["POST"])
def callback():
    # Line message header
    signature = request.headers["X-Line-Signature"]
    # ask data
    body = request.get_data(as_text=True)
    try:
        # handle message
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

# handle line message
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # check user whether in DB
    DB.check_userID(event.source.user_id)

    # get line message, help or dialogflow
    message = event.message.text
    if message.strip() == '?' or message.strip() == '？':
        f = open("../data/questionMark.txt", 'r', encoding="UTF-8")
        line_bot_api.push_message(
            DB.get_userID(), TextSendMessage(text=f.read()))
        f.close()
    else:
        dialog_req(message)
    pass

# connect and send message to dialogflow then get response
def dialog_req(message):
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
    request = ai.text_request()
    request.lang = 'tw'
    request.query = message
    response = request.getresponse().read().decode()
    webhook(json.loads(response))

def webhook(response):
    parameters = response['result']['parameters']
    # check user input event
    events = {
        "電腦": DB.computer_list,
        "排序": DB.computer_list,
        "變更": DB.change_attention_list,
        "關注資料": DB.attention_list,
        "特價": DB.computer_discount,
    }
    message = {1: parameters['result']['fulfillment']['speech']}
    intent = response['result']['metadata']['intentName']
    for key, func in events.items():
        if key in intent:
            message = func(key, parameters)
            break
    for mes in message.values():
        line_bot_api.push_message(DB.get_userID(), TextSendMessage(text=mes))

if __name__ == "__main__":
    app.run(port=5000)