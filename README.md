# DSBMobileBot
Gather timetable data from DSBMobile.

## Scraper
This scraper gathers the data and saves it to json/groupedtables.json
1. make container with scraper/make_docker_container.sh 
2. run the container with ./get_data_docker.sh

## Telegram Bot
You can get messaged by the bot with your current timetable data. Try it out: `@DSBMobile_Bot`.

### Usage
- To **configure** the bot supply DSBMobile username and password via the commands: `/setdsbuser`, `/setdsbpassword`.
- To get **your specific** timetable specify your classname via the command: `/setclassname`
- To get your **timetable data** user: `/update`.

### Development
add `config.py` with the folling values to `telegram-bot/`

```
ngrok_url = <ENDPOINT_FOR_TELEGRAM_API> # for local dev
aws_url = <ENDPOINT_FOR_TELEGRAM_API> # for production use
bot_token = <TELEGRAM_BOT_TOKEN>
s3_bucket_name = <AMAZON_AWS_S3_BUCKET_NAME_FOR_STORAGE>
```
