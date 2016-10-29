import os
import sys
import json

import requests
from flask import Flask, request
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

app = Flask(__name__)

realli_bot = ChatBot(
  "Realli Bot",
)

with open("./data/conversations.json", "rb") as json_data:
  conversations = json.load(json_data)['conversations']

with open("./data/property.json", "rb") as json_data:
  property_data = json.load(json_data)['property']

realli_bot.set_trainer(ListTrainer)

realli_bot.train(
  conversations[0]
)

realli_bot.train(
  property_data[0]
)


@app.route('/', methods=['GET'])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200

@app.route('/get/<string:query>', methods=['GET'])
def test(query):
    resp = str(realli_bot.get_response(query))
    return resp, 200

@app.route('/send', methods=['GET'])
def send():
    msg = request.args.get("msg")
    print(msg)
    resp = str(english_bot.get_response(msg))
    return resp, 200

@app.route('/', methods=['POST'])
def webhook():

    data = request.get_json()
    log(data)

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):
                    sender_id = messaging_event["sender"]["id"]
                    recipient_id = messaging_event["recipient"]["id"]
                    message_text = messaging_event["message"]["text"]

                    #parsing the message and formulating the answer will be done
                    #here.
                    send_message(sender_id, "got it, thanks!")

                if messaging_event.get("delivery"):
                    pass

                if messaging_event.get("optin"):
                    pass

                if messaging_event.get("postback"):
                    pass

    return "ok", 200


def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):
    print(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
