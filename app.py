from flask import Flask, request, Response
import requests, json, random, os
import cloudinary, pymongo
from pymongo import MongoClient

app = Flask(__name__)

# env_variables
# token to send messages through facebook messenger
PAGE_ACCESS_TOKEN = os.getenv('ACCESS_TOKEN', None)
# token to verify that this bot is legit
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN', None)

#PAGE_ACCESS_TOKEN = 'EAAfdfGQccFQBAEQz2z2dZAMGaF3x5WlpG1YcaPJCMs0EU8sEPqdjetkWCzGf69FUa7mMwDZCJsg8VGy5VcpyMkc7VtV9p4Nyzi7s9QeXyggMTwjjSKHZBTZAoPzrhhSQdP8gDsiRtbEyG1LgVH3uCE29ZCfsfKwhPg8ZBadxjYCwZDZD'
#VERIFY_TOKEN = '8d831a1a-22a0-4899-bb56-9f468c531bf9'

@app.route('/', methods=['GET'])
def handle_verification():
    if (request.args.get('hub.verify_token', '') == VERIFY_TOKEN):
        print("Verified")
        return request.args.get('hub.challenge', '')
    else:
        print("Wrong token")
        return "Error, wrong validation token"


def send_message_response(sender_id, message_text):
    sentenceDelimiter = ". "
    messages = message_text.split(sentenceDelimiter)

    for message in messages:
        send_message(sender_id, message)


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


def send_image(sender_id, image_url):
    '''
    Sending response back to the user using facebook graph API
    '''
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",

        params={"access_token": PAGE_ACCESS_TOKEN},

        headers={"Content-Type": "application/json"},

        data=json.dumps({
        "recipient": {"id": sender_id},
        "message": {
          "attachment":{
            "type":"image",
            "payload":{
              "url":image_url,
              "is_reusable":True
            }
          }
        }
    }))

@app.route('/', methods=['POST'])
def handle_message():
    '''
    Handle messages sent by facebook messenger to the application
    '''
    data = request.get_json()
    #attachments = []
    #if data["object"] == "page":
    for entry in data["entry"]:
        for messaging_event in entry["messaging"]:
            if messaging_event.get("message"):
                sender_id = messaging_event["sender"]["id"]
                recipient_id = messaging_event["recipient"]["id"]
                set_default_settings(sender_id)
                if "text" in messaging_event["message"]:
                    message_text = messaging_event["message"]["text"]
                    send_message_response(sender_id, message_text)
                    setting_listener(sender_id, message_text)

                    if "send image" in message_text:
                        group_id = return_group_id(sender_id)
                        if db["user"].count_documents({"group_id":group_id}) > 0:
                            send_image(sender_id, find_group_image(group_id))

                if "attachments" in messaging_event["message"]:
                    for attachment in messaging_event["message"]["attachments"]:
                        attachment_link = attachment["payload"]["url"]
                        #send_message_response(sender_id, attachment_link)
                        add_image(sender_id, return_group_id(sender_id), attachment_link)
                        if "attachment_id" in attachment:
                            attachment_id = attachment["payload"]["attachment_id"]
                            send_message(sender_id, attachment_id)

    return "ok"

mongo_db_pass = "rfgcbsD7q6jnYaJZ"
cluster = MongoClient("mongodb+srv://jackculpan:{}@cluster0-qnac0.mongodb.net/pupdate?retryWrites=true&w=majority".format(mongo_db_pass))
db = cluster["pupdate"]

def add_image(user_id, group_id, image_url):
    #mongo_db_pass = os.getenv('MONGODB', None)
    collection = db["user"]
    post = {"group_id":group_id, "user_id": str(user_id), "image_url": str(image_url)}
    collection.insert_one(post)

def find_image(user_id):
    collection = db["user"]
    count = collection.count_documents({"user_id":user_id})
    results = collection.find({"user_id":user_id})
    result = results[random.choice(range(count))]
    return result["image_url"]

def find_group_image(group_id):
    collection = db["user"]
    count = collection.count_documents({"group_id":group_id})
    results = collection.find({"group_id":group_id})
    result = results[random.choice(range(count))]
    return result["image_url"]

def setting_listener(user_id, message_text):
    if "==" in message_text:
        sentenceDelimiter = "=="
        messages = message_text.split(sentenceDelimiter)
        setting, value = messages[0], messages[1]
        if setting == "frequency":
            set_frequency(user_id, value) #need to turn value into integer from string
        elif setting == "group_id":
            set_group_id(user_id, value)

def set_default_settings(user_id):
    set_frequency(user_id, "one_day")
    set_group_id(user_id, user_id)

def set_frequency(user_id, value):
    post = {"_id": str(user_id), "frequency": value}
    collection = db["settings"]
    collection.insert_one(post)
    send_message(user_id, "frequency changed")

def return_frequency(user_id):
    collection = db["settings"]
    result = collection.find_one({"_id":user_id})
    return result["frequency"]

def set_group_id(user_id, value):
    post = {"_id": str(user_id), "group_id": value}
    collection = db["settings"]
    collection.insert_one(post)
    send_message(user_id, "group id changed")

def return_group_id(user_id):
    collection = db["settings"]
    result = collection.find_one({"_id":user_id})
    return result["group_id"]

def send_frequency(user_id):
    #def job():
    #sender_id = "2540997945998584"
    #count = collection.count_documents({"user_id":"one"})
    #print(count)
    #send_message(sender_id, find_image(sender_id))
    freq = return_frequency(user_id)
    if freq == "three_day":
        schedule.every(1).day.at("08:30").do(job(user_id))
        schedule.every(1).day.at("12:30").do(job(user_id))
        schedule.every(1).day.at("16:30").do(job(user_id))
    elif freq == "one_day":
        schedule.every(1).day.at("12:30").do(job(user_id))
    elif freq == "one_week":
        schedule.every(1).wednesday.at("13:15").do(job(user_id))

def job(user_id):
    group_id = return_group_id(user_id)
    send_image(user_id, find_group_image(group_id))



@app.route('/webhook_dev', methods=['POST'])
def webhook_dev():
    # custom route for local development
    '''
    Handle messages sent by facebook messenger to the application
    '''
    data = request.get_json()
    #attachments = []
    #if data["object"] == "page":
    for entry in data["entry"]:
        for messaging_event in entry["messaging"]:
            if messaging_event.get("message"):
                sender_id = messaging_event["sender"]["id"]
                recipient_id = messaging_event["recipient"]["id"]
                if "text" in messaging_event["message"]:
                    message_text = messaging_event["message"]["text"]
                    send_message_response(sender_id, message_text)
                if "attachments" in messaging_event["message"]:
                    for attachment in messaging_event["message"]["attachments"]:
                        attachment_link = attachment["payload"]["url"]
                        #send_message_response(sender_id, attachment_link)
                        add_image(sender_id, attachment_link)
                        send_image(sender_id, attachment_link)
                        if "attachment_id" in attachment:
                            attachment_id = attachment["payload"]["attachment_id"]
                            send_message_response(sender_id, attachment_id)

    return "ok"

def handle_dev_message(user_id, user_message):
    # DO SOMETHING with the user_message ... ¯\_(ツ)_/¯
    return "Hello "+user_id+" ! You just sent me : " + user_message

if __name__ == '__main__':
    app.run()
    #while True:
        #schedule.run_pending()
        #time.sleep(1)
