from flask import Flask, request, Response
import requests, json, random, os
import cloudinary

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
              "is_reusable":true
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
    attachments = []
    #if data["object"] == "page":
    for entry in data["entry"]:
        for messaging_event in entry["messaging"]:
            if messaging_event.get("message"):
                sender_id = messaging_event["sender"]["id"]
                recipient_id = messaging_event["recipient"]["id"]
                if "text" in messaging_event["message"]:
                    message_text = messaging_event["message"]["text"]
                    send_message_response(sender_id, message_text)

                if messaging_event["message"].get("attachment"):
                    attachment_link = messaging_event["message"]["attachment"]["payload"]["url"]
                    upload_image(sender_id, attachment_link)
                #if messaging_event["message"].get("attachments"):
                    #for attachment in messaging_event["message"]["attachments"]:
                        #attachments.append(attachment["payload"]["url"])
    return "ok"

def upload_image(user_id, url):
    #cloudinary.uploader.unsigned_upload(url, str(count_files(user_id)),
    #cloud_name = 'dyigdenkz')

    cloudinary.config = ({
        'cloud_name':os.getenv('CLOUDINARY_CLOUD_NAME', None),
        'api_key': os.getenv('CLOUDINARY_API_KEY', None),
        'api_secret': os.getenv('CLOUDINARY_API_SECRET', None)
    })

    #public_id="https://res.cloudinary.com/dyigdenkz/pupdate/"
    cloudinary.uploader.upload(url)
    cloudinary.uploader.unsigned_upload(url, ml_default)
    return "ok"
    #, folder=user_id
    #post_url = "https://api.cloudinary.com/v1_1/dyigdenkz/auto/upload"
    #file = url
    #api_key = os.getenv('CLOUDINARY_KEY', None)
    #timestamp = time()

#def upload_images():
    #image = CloudinaryJsFileField(
    #attrs = { 'multiple': 1 })


#def count_files(user_id):
    #cloudinary.api.subfolders("pupdate/{}".format(user_id))

    #result = cloudinary.Search()
        #.expression('folder={}'.format(user_id))
        #.sort_by('public_id','desc')
        #.aggregate('format')
        #.execute()
    #count = count(result)
    #"https://res.cloudinary.com/dyigdenkz/image/list/user_id.json"

    #count number of files
    #+1 to that for file name
    #return count+1




def send_message_response(sender_id, message_text):
    sentenceDelimiter = ". "
    messages = message_text.split(sentenceDelimiter)

    for message in messages:
        send_message(sender_id, message)


@app.route('/webhook_dev', methods=['POST'])
def webhook_dev():
    # custom route for local development
    #data = json.loads(request.data.decode('utf-8'))
    #user_message = data['entry'][0]['messaging'][0]['message']['text']
    #user_id = data['entry'][0]['messaging'][0]['sender']['id']
    data = request.get_json()

    #if data["object"] == "page":
    for entry in data["entry"]:
        for messaging_event in entry["messaging"]:
            if messaging_event.get("message"):
                sender_id = messaging_event["sender"]["id"]
                recipient_id = messaging_event["recipient"]["id"]
                message_text = messaging_event["message"]["text"]
                send_message_response(sender_id, message_text)

                if messaging_event["message"].get("attachment"):
                    attachment_link = messaging_event["message"]["attachment"]["payload"]["url"]
                    send_image(sender_id, attachment_link)
    return "ok"

def handle_dev_message(user_id, user_message):
    # DO SOMETHING with the user_message ... ¯\_(ツ)_/¯
    return "Hello "+user_id+" ! You just sent me : " + user_message

if __name__ == '__main__':
    app.run()
