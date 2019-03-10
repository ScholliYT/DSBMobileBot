import requests
from flask import Flask, request
from telepot.exception import TelegramError
import boto3
import botocore
import traceback
import json
import config
import dsbmobil_scraper

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

def getConfigFile(chat_id, nofitify_on_missing = True):
    try:
        s3 = boto3.client("s3")
        response = s3.get_object(Bucket=config.s3_bucket_name, Key=getS3Path(chat_id, "config.json"))
        data = response['Body'].read().decode('utf-8')
        jsonconfig = json.loads(str(data))
        return jsonconfig
    except Exception as e:
        if(nofitify_on_missing):
            sendMessage(chat_id, "Sorry! Ich konnte keine Konfiguration finden.")
        return None

def updateConfigValue(chat_id, key, value):
    jsonconfig = getConfigFile(chat_id, False)
    if jsonconfig:
        jsonconfig[key] = value
    else:
        jsonconfig = {key: value}

    encoded_config = json.dumps(jsonconfig, ensure_ascii=False).encode("utf-8")
    s3 = boto3.resource("s3")
    s3.Bucket(config.s3_bucket_name).put_object(Key=getS3Path(chat_id, "config.json"), Body=encoded_config)

def process_message(message):
    print("message: " + str(message))
    chat_id = message["chat"]["id"]
    try:
        if "text" in message:
            text = message["text"]
            if "@DSBMobile_Bot" in text:
                text = text.replace("@DSBMobile_Bot", "")
            if text == "/update":
                jsonconfig = getConfigFile(chat_id)
                if jsonconfig:
                    if all (k in jsonconfig for k in ("dsbuser", "dsbpassword")):
                        dsbmobile =  dsbmobil_scraper.DSBMobile(jsonconfig["dsbuser"], jsonconfig["dsbpassword"])
                        if(dsbmobile.auth()):
                            groupedtables = dsbmobil_scraper.getNewData(dsbmobile)
                            if "class" in jsonconfig:
                                response_message = ""
                                for day in groupedtables:
                                    if jsonconfig["class"] in groupedtables[day]:
                                        classname = jsonconfig["class"]
                                        response_message = response_message + "\nAm *" + day + "* sind folgende Vertretungen:"+"\n"
                                        for sub in groupedtables[day][jsonconfig["class"]]:
                                            response_message = response_message + str(sub) +"\n"
                                    else:
                                        response_message = response_message + "\nAm *" + day + "* sind keine Vertretungen."+"\n\n"
                                sendMessage(chat_id, response_message)
                            else:
                                sendMessage(chat_id, "Da keine Klasse konfiguriert ist, werden alle Daten ausgegeben")
                                sendMessage(chat_id, str(groupedtables))
                        else:
                            sendMessage(chat_id, "Benutzername oder Passwort falsch")
                    else:
                        sendMessage(chat_id, "Benutzer oder Passwort ist nicht konfiguriert")
            elif text == "/help":
                sendMessage(chat_id, """Dies ist ein Bot um daten von DSBmobile zu empfangen.
                    \nBei übermäßiger Nutzung entstehen exorbitante Kosten, weil dieser Bot über Amazon AWS betrieben wird.
                    \nGithub: https://github.com/ScholliYT/DSBMobileBot""")
            elif text.startswith("/setclass"): 
                classname = text.replace("/setclass ", "")
                if not classname:
                    raise Exception('invalid arguments')

                updateConfigValue(chat_id, "class", classname)
                sendMessage(chat_id, "Ich habe die Klasse: \"" + classname + "\" gespeichert.")
            elif text == "/getclass":
                jsonconfig = getConfigFile(chat_id)
                if jsonconfig:
                    if "class" in jsonconfig:
                        sendMessage(chat_id, "Die konfigurierte Klasse ist: " + jsonconfig["class"])
                    else:
                        sendMessage(chat_id, "Es ist keine Klasse konfiguriert")
            elif text.startswith("/setdsbuser"): 
                dsbuser = text.replace("/setdsbuser ", "")
                if not dsbuser:
                    raise Exception('invalid arguments')

                updateConfigValue(chat_id, "dsbuser", dsbuser)
                sendMessage(chat_id, "Ich habe den Benutzernamen: \"" + dsbuser + "\" gespeichert.")
            elif text == "/getdsbuser":
                jsonconfig = getConfigFile(chat_id)
                if jsonconfig:
                    if "dsbuser" in jsonconfig:
                        sendMessage(chat_id, "Der konfigurierte Benutzer für DSBMobile ist: " + jsonconfig["dsbuser"])
                    else:
                        sendMessage(chat_id, "Es ist kein Benuzter konfiguriert")
            elif text.startswith("/setdsbpassword"): 
                dsbpassword = text.replace("/setdsbpassword ", "")
                if not dsbpassword:
                    raise Exception('invalid arguments')

                updateConfigValue(chat_id, "dsbpassword", dsbpassword)
                sendMessage(chat_id, "Ich habe das Passwort: \"" + dsbpassword + "\" gespeichert.")
            elif text == "/getdsbpassword":
                jsonconfig = getConfigFile(chat_id)
                if jsonconfig:
                    if "dsbpassword" in jsonconfig:
                        sendMessage(chat_id, "Das konfigurierte Passwort für DSBMobile ist: " + jsonconfig["dsbpassword"])
                    else:
                        sendMessage(chat_id, "Es ist kein Passwort konfiguriert")    
            else:
                sendMessage(chat_id, "Bitte entschuldige. Das habe ich nicht verstanden.")
    except Exception:
        print(traceback.format_exc())
        sendMessage(chat_id, text="Bitte entschuldige. Es ist ein Fehler aufgetreten.")

@app.route("/{}".format(config.bot_token), methods=["POST"])
def process_update(): # entry point for requests coming from Telegram API
    if request.method == "POST":
        update = request.get_json()
        if "message" in update:
            process_message(update["message"])
        return "ok!", 200
    return request.method + " is not supported", 502
