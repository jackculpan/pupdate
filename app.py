from flask import Flask, request, Response
import requests, json, random, os
app = Flask(__name__)

# env_variables
# token to verify that this bot is legit
verify_token = os.getenv('VERIFY_TOKEN', None)
# token to send messages through facebook messenger
access_token = os.getenv('ACCESS_TOKEN', None)

PAGE_ACCESS_TOKEN = 'EAAIZBVzmu74kBACrIp73309ZChRPo8B5ZBNZA9zlsEXom4vnpeTCRvpZC8WNPZAsNif94RaP7QvCWhONh2dhYSxkNOelwgV56SnRA6wuo6zxcX0etFjxeza8dWz0cZAHEo21tuiaNKWgvsr4XCZAFUnmDJPS0o3LJQoqE0IZBx7WBvAZDZD'
VERIFY_TOKEN = '978abb1eadb9aa6c841abdb95429cda479adf571dc455077dce9cd9e4fb7a9d6'

@app.route('/', methods=['GET'])
def handle_verification():
    if (request.args.get('hub.verify_token', '') == VERIFY_TOKEN):
        print("Verified")
        return request.args.get('hub.challenge', '')
    else:
        print("Wrong token")
        return "Error, wrong validation token"

def send_message(sender_id, message_text):
    '''
    Sending response back to the user using facebook graph API
    '''
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",

        params={"access_token": PAGE_ACCESS_TOKEN},

        headers={"Content-Type": "application/json"},

        data=json.dumps({
        "recipient": {"id": sender_id},
        "message": {"text": message_text}
    }))

@app.route('/', methods=['POST'])
def handle_message():
    '''
    Handle messages sent by facebook messenger to the applicaiton
    '''
    data = request.get_json()

    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):

                    sender_id = messaging_event["sender"]["id"]
                    recipient_id = messaging_event["recipient"]["id"]
                    message_text = messaging_event["message"]["text"]
                    send_message_response(sender_id, message_text)
                if entry["message"].get("attachments"):
                    attachment_link = entry["message"]["attachments"][0]["payload"]["url"]
                    send_message_response(sender_id, attachment_link)
    return "ok"

def send_message_response(sender_id, message_text):
    sentenceDelimiter = ". "
    messages = message_text.split(sentenceDelimiter)

    for message in messages:
        send_message(sender_id, message)

if __name__ == '__main__':
    app.run()
