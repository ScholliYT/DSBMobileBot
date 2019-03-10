from pprint import pprint
import requests
import config

test_url = config.ngrok_url + "/{}".format(config.bot_token)

def get_url(method):
    return "https://api.telegram.org/bot{}/{}".format(config.bot_token,method)

r = requests.get(get_url("setWebhook"), data={"url": test_url})
r = requests.get(get_url("getWebhookInfo"))
pprint(r.status_code)
pprint(r.json())
