import json
import requests

from BotConnection import BotController as controller

SESSION_FILES = []


# - - - - - - - - - - - - - - - - - - - - - - CUSTOM METHODS - - - - - - - - - - - - - - - - - - - - - - #
# reports message/takes action if file uploaded meets certain criteria
def report_file_shared(data):

    keywords = ['performance', 'ratings', 'production', 'fitch', 'collaboration']

    file_obj = controller.on_file_shared(data)

    keyword_in_file = filter(lambda x: x in file_obj['file']['name'], keywords)

    # if file has already been documented, then skip it
    if file_obj['file']['name'] in SESSION_FILES:
        print ('ERROR: FILE ALREADY HANDLED')
        return

    # else, check if it is over 25 MB OR if it contains certain keywords
    # if either case matches, alert channel
    else:
        # if file > 25 MB post a message
        if file_obj['file']['size'] > 25000000:
            payload = json.dumps(controller.message_builder("File Size Larger Than 25MB",
                                                            "File ID: " + file_obj['file']['id'] + "\n File Name: " + file_obj['file']['name'] +
                                                            "\n User ID: " + file_obj['file']['user'],
                                                            controller.get_user_real_name(file_obj['file']['user'])))
            requests.post(controller.WEB_HOOK, data=payload)

            # TODO: add message to admin channel

        # if the keyword does exist in the file then post a message
        if keyword_in_file:
            payload = json.dumps(controller.message_builder("File found with keyword: " + ''.join(keyword_in_file),
                                                            "File ID: " + file_obj['file']['id'] + "\n File Name: " + file_obj['file']['name'] +
                                                            "\n User ID: " + file_obj['file']['user'],
                                                            controller.get_user_real_name(file_obj['file']['user'])))
            requests.post(controller.WEB_HOOK, data=payload)

        # add file name to list which will be cross-referenced next time a file is uploaded
        # this is to detect any duplication
        SESSION_FILES.append(file_obj['file']['name'])


# gets user info based on user ID
def report_if_fitch_user(data):

    channel_obj = controller.on_channel_created(data)
    user_obj = controller.get_user_obj(channel_obj['channel']['creator'])

    if 'fitchratings' in user_obj['user']['profile']['email']:
        controller.post_message_from_listener('channel_created', channel_obj)
        controller.post_simple_message(controller.CHANNEL, 'Channel Created By Fitch User')
        controller.post_simple_message(controller.CHANNEL, 'User Email: ' + user_obj['user']['profile']['email'])

# - - - - - - - - - - - - - - - - - - - - - - END CUSTOM METHODS - - - - - - - - - - - - - - - - - - - - - - #


# reads the json data stream and handles events
def event_handler(data_, res_):
    # alerts channel if another channel is created
    if "channel_created" in res_:
        report_if_fitch_user(data_)

    # alerts channel if a file uploaded
    if "file_shared" in res_:
        report_file_shared(data_)

    # calls command handler if a message is entered in slack
    if "message" in res_:
        controller.command_handler(data_)

# # # - - - - - - - - - - MAIN RTM LOOP - - - - - - - - - - # # #

rtm_stream = controller.get_connection_stream()

while True:
    try:
        res = rtm_stream.recv()
        data = json.loads(res)

        event_handler(data, res)

    except Exception as e:
        print 'exception: ' + e.message

    # The below statement commented out but can be uncommented for logging/debugging purposes
    # It prints out a log of all events occurring to the console
    # print(res)
# # # - - - - - - - - - - END MAIN RTM LOOP - - - - - - - - - - # # #

