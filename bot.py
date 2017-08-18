from BotConnection import BotController as controller

SESSION_FILES = []


# - - - - - - - - - - - - - - - - - - - - - - CUSTOM METHODS - - - - - - - - - - - - - - - - - - - - - - #


# - - - - - - - - - - - - - - - - - - - - - - END CUSTOM METHODS - - - - - - - - - - - - - - - - - - - - - - #


# reads the json data stream and handles events
def event_handler(data_, res_):
    # handle events

# # # - - - - - - - - - - MAIN RTM LOOP - - - - - - - - - - # # #

rtm_stream = controller.get_connection_stream()

while True:
    try:
        res = rtm_stream.recv()
        data = json.loads(res)

        event_handler(data, res)
        controller.command_listener(data, res)

    except Exception as e:
        print 'exception: ' + e.message

    # The below statement commented out but can be uncommented for logging/debugging purposes
    # It prints out a log of all events occurring to the console
    # print(res)
# # # - - - - - - - - - - END MAIN RTM LOOP - - - - - - - - - - # # #

