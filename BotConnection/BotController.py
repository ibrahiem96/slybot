import json
import requests
import sys
import os
from slacker import Slacker
from websocket import create_connection

SLACK = Slacker(os.environ.get('API_TOKEN'))
WEB_HOOK = os.environ.get('WEB_HOOK')
BOT = os.environ.get('BOT_NAME')
CHANNEL = os.environ.get('CHANNEL_NAME')

BOT_ID = SLACK.users.get_user_id(BOT)


# - - - - - - - - - - - HELPER METHODS - - - - - - - - - - - #
# builds message in json format
def message_builder(title, summary, author):
    json_obj = {
        "attachments": [
            {
                "title": title,
                "color": "#36a64f",
                "text": summary,
                "author_name": ('By: '+author)
            }
        ]
    }
    return json_obj


def post_simple_message(channel_name, message):
    SLACK.chat.post_message(channel_name, message)


def get_channel(channelid):
    return SLACK.channels.info(channelid).body


def get_user_obj(userid):
    return SLACK.users.info(userid).body


def get_user_real_name(userid):
    user_obj = get_user_obj(userid)
    return user_obj['user']['profile']['real_name']


def get_file_obj(fileid):
    return SLACK.files.info(fileid).body


def on_channel_created(data):

    channel_id = data['channel']['id']
    channel_obj = get_channel(channel_id)
    return channel_obj


def on_file_shared(data):
    file_id = data['file_id']
    file_obj = get_file_obj(file_id)
    return file_obj


def get_connection_stream():
    session = SLACK.rtm.start()
    url = session.body['url']
    ws = create_connection(url)
    res = ws.recv()
    rep = json.loads(res)

    # checks if connection with RTM API is successful
    if rep['type'] == 'hello':
        print('connected successfully')
        payload = json.dumps(message_builder("Bot Connected Successfully",
                                             "Slybot listens to programmed events and will give you feedback based on"
                                             "certain events occurring."
                                             " If you want the slackbot to carry out a command, simply message the bot with"
                                             " its handle, i.e: @botname hello",
                                             BOT))
        requests.post(WEB_HOOK, data=payload)

    return ws


def command_handler(data):
    message = data['text']

    if BOT_ID in message:

        if "disconnect" in message:
            SLACK.chat.post_message(CHANNEL, "Goodbye!")
            print 'disconnecting...'
            sys.exit()

        elif "hello" in message:
            SLACK.chat.post_message(CHANNEL, "Hello! Enter in the command 'help' to see what I can do for you")

        elif "help" in message:
            payload = json.dumps(message_builder("Commands",
                                                 "disconnect: disconnects the specified bot from slack\n"
                                                 "hello: responds with hello", BOT))
            requests.post(WEB_HOOK, data=payload)

        else:
            SLACK.chat.post_message(CHANNEL, "Command not understood")


def post_message_from_listener(event_type, data):
    if event_type is 'channel_created':
        payload = json.dumps(message_builder("Channel Created",
                                             "Channel ID: " + data['channel']['id'] + "\n Channel Name: " +
                                             data['channel']['name'] + "\n Creator ID: " +
                                             data['channel']['creator'],
                                             get_user_real_name(data['channel']['creator'])))
        requests.post(WEB_HOOK, data=payload)

    elif event_type is 'user_created':
        payload = json.dumps(message_builder("User Created",
                                             "User ID: " + data['user']['id'] + "\n User Name: " +
                                             data['user']['profile']['name'] + "\n User Email: " +
                                             data['user']['profile']['email'],
                                             get_user_real_name(data['channel']['creator'])))
        requests.post(WEB_HOOK, data=payload)

    else:
        print ('invalid event type')


# # - - - - - - - - - - - END HELPER METHODS - - - - - - - - - - - #

