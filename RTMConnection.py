import json
import requests
from slacker import Slacker
from websocket import create_connection

from BotActions.settings import API_TOKEN, WEB_HOOK, ChannelsToPostTo

slack = Slacker(API_TOKEN)
channels = ChannelsToPostTo()

session = slack.rtm.start()
url = session.body['url']
ws = create_connection(url)
res = ws.recv()
rep = json.loads(res)

session_files = []


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

# checks if connection with RTM API is successful
if rep['type'] == 'hello':
    print('connected successfully')
    payload = json.dumps(message_builder("Bot Connection",
                                         "Bot Connected Successfully",
                                         "ibrahiembot"))
    requests.post(WEB_HOOK, data=payload)


# - - - - - - - - - - - - - - - - - - - - - - CUSTOM METHODS - - - - - - - - - - - - - - - - - - - - - - #

# reports message/takes action if file uploaded meets certain criteria
def report_file_shared(data):

    keywords = ['performance', 'ratings', 'production', 'fitch', 'collaboration']

    file_id = data['file_id']
    file_obj = get_file_obj(file_id)

    keyword_in_file = filter(lambda x: x in file_obj['file']['name'], keywords)

    # if file has already been documented, then skip it
    if file_obj['file']['name'] in session_files:
        print ('ERROR: FILE ALREADY HANDLED')
        return

    # else, check if it is over 25 MB OR if it contains certain keywords
    # if either case matches, alert channel
    else:
        if file_obj['file']['size'] > 25000000:
            payload = json.dumps(message_builder("File Size Larger Than 25MB",
                                 "File ID: " + file_obj['file']['id'] + "\n File Name: " + file_obj['file']['name'] +
                                                 "\n User ID: " + file_obj['file']['user'],
                                                 get_user_real_name(file_obj['file']['user'])))
            requests.post(WEB_HOOK, data=payload)

            # TODO: add message to admin channel

        if keyword_in_file:
            payload = json.dumps(message_builder("File found with keyword: " + ''.join(keyword_in_file),
                                                 "File ID: " + file_obj['file'][
                                                     'id'] + "\n File Name: " + file_obj['file']['name'] +
                                                 "\n User ID: " + file_obj['file']['user'],
                                                 get_user_real_name(file_obj['file']['user'])))
            requests.post(WEB_HOOK, data=payload)

        # add file name to list which will be cross-referenced next time a file is uploaded
        # this is to detect any duplication
        session_files.append(file_obj['file']['name'])


# gets user info based on user ID
def report_if_fitch_user(data):

    channel_obj = on_channel_created(data)
    user_obj = get_user_obj(channel_obj['channel']['creator'])

    if 'fitchratings' in user_obj['user']['profile']['email']:
        post_message_from_listener('channel_created', channel_obj)
        post_simple_message(channels.bot_testing_arena, 'Channel Created By Fitch User')
        post_simple_message(channels.bot_testing_arena, 'User Email: ' + user_obj['user']['profile']['email'])

# - - - - - - - - - - - - - - - - - - - - - - END CUSTOM METHODS - - - - - - - - - - - - - - - - - - - - - - #


# - - - - - - - - - - - HELPER METHODS - - - - - - - - - - - #


def post_simple_message(channel_name, message):
    slack.chat.post_message(channel_name, message)


def get_channel(channelid):
    return slack.channels.info(channelid).body


def get_user_obj(userid):
    return slack.users.info(userid).body


def get_user_real_name(userid):
    user_obj = get_user_obj(userid)
    return user_obj['user']['profile']['real_name']


def get_file_obj(fileid):
    return slack.files.info(fileid).body


def on_channel_created(data):

    channel_id = data['channel']['id']
    channel_obj = get_channel(channel_id)
    return channel_obj


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


# - - - - - - - - - - - END HELPER METHODS - - - - - - - - - - - #
# reads the json data stream and handles events
def event_handler(data_, res_):
    # alerts channel if another channel is created
    if "channel_created" in res_:
        report_if_fitch_user(data_)

    # alerts channel if a file uploaded
    if "file_shared" in res_:
        report_file_shared(data_)


# # # - - - - - - - - - - MAIN RTM LOOP - - - - - - - - - - # # #
while True:
    try:
        res = ws.recv()
        data = json.loads(res)

        event_handler(data, res)

    except Exception as e:
        print 'exception: ' + e.message

    # The below statement commented out but can be uncommented for logging/debugging purposes
    # It prints out a log of all events occurring to the console
    #print(res)
# # # - - - - - - - - - - END MAIN RTM LOOP - - - - - - - - - - # # #
