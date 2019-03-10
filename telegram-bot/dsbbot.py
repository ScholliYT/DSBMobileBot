import requests
from flask import Flask, request
from telepot.exception import TelegramError
import boto3
import traceback
import config

app = Flask(__name__)

def getS3Path(chat_id, filename):
    return "data/" + str(chat_id) + "/" + str(filename)

def get_url(method):
  return "https://api.telegram.org/bot{}/{}".format(config.bot_token,method)

def sendMessage(chat_id, text, parse_mode = "Markdown"):
    data = {}
    data["chat_id"] = chat_id
    data["parse_mode"] = parse_mode
    data["text"] = text
    r = requests.post(get_url("sendMessage"), data=data)

def process_message(message):
    chat_id = message["chat"]["id"]
    try:
        if "text" in message:
            text = message["text"]
            if "@DSBMobile_Bot" in text:
                text = text.replace("@DSBMobile_Bot", "")
            if text == "/help":
                sendMessage(chat_id, """Dies ist ein Bot um daten von DSBmobile zu empfangen.
                    \nBei übermäßiger Nutzung entstehen exorbitante Kosten, weil dieser Bot über Amazon AWS betrieben wird.
                    \nGithub: https://github.com/ScholliYT/DSBMobileBot""")
            elif text.startswith("/store"): 
                string = text.replace("/store ", "")
                encoded_string = string.encode("utf-8")

                s3 = boto3.resource("s3")
                s3.Bucket(config.s3_bucket_name).put_object(Key=getS3Path(chat_id, "config.txt"), Body=encoded_string)
                sendMessage(chat_id, "Habe: \"" + string + "\" gespeichert.")
            elif text == "/get":
                s3 = boto3.client("s3")
                response = s3.get_object(Bucket=config.s3_bucket_name, Key=getS3Path(chat_id, "config.txt"))
                data = response['Body'].read().decode('utf-8')

                sendMessage(chat_id, data)
            else:
                sendMessage(chat_id, "Bitte entschuldigen Sie. Das habe ich nicht verstanden.")
    except Exception:
        print(traceback.format_exc())
        sendMessage(chat_id, text="Bitte entschuldigen Sie. Es ist ein Fehler aufgetreten.")

@app.route("/{}".format(config.bot_token), methods=["POST"])
def process_update(): # entry point for requests coming from Telegram API
    if request.method == "POST":
        update = request.get_json()
        if "message" in update:
            process_message(update["message"])
        return "ok!", 200
    return request.method + " is not supported", 502
