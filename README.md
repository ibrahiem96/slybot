


# Getting Started with Slython Slackbot API
&nbsp;&nbsp; Slython is a slackbot that builds upon the slacker python library to connect a bot to a slack team. It also connects with the RTM API to get real time events and report on those events.


# Table of Contents
1. [Setup](#setup)
  1a. [Configuration](#configuration)
2. [Usage](#usage)
3. [Methods](#methods)


##### What works in this version
&nbsp;&nbsp; As of right now Slython has the following functionality:
1. Connects to rtm and subscribes to any and all events that transpire on your slack team.
2. The API actively acknowledges and sends a message to #bot_testing_arena everytime a channel is created.
3. Reports if a channel is created and if channel creator is a fitch user
4. Reports if a file uploaded is greater than 25MB
5. Can run from a docker file
6. Integrated with Webhook URL to provide pretty-formatted JSON messages in channels.
7. Command handler (slackbot can listen to commands and carry them out)
8. Client code

##### Goals for the future
1. Determine if slack notifications/settings are accessible by bot; if so, subscribe to and interact with notification
2. Events should be handled outside of client code
3. Add interaction with multiple channels

## Setup
##### Requirements
1. Python 2.7

##### Configuration
**NOTE: Step 2-4 are not necessary if you are using the bitbucket repository (the environment variables are added to the
bamboo build plan**
1. Clone the repo and go inside the directory
2. Enter the following commands
```bash
export API_TOKEN="<api token here>"
```
If you need help creating a bot and its token, [use this guide](https://imperiallabs.github.io/quick_landing.html#get-a-key).
```bash
export WEB_HOOK="<web hook url here>"
```
If you need assistance in setting up an incoming webhook URL, [go here]( https://slack.com/apps/manage/custom-integrations), and click on the incoming webhooks option.
```bash
export BOT_NAME="<bot username>" # this is the same username you registered the bot with
export CHANNEL_NAME="<channel name here>" # obviously the bot can interact with any channel, but this here is the channel that it is invited to.
```
3. Add any libraries you are going to use to the requirements.txt file

##### Running Locally (without Docker)

1. Once setup is configured click run if you are using PyCharm or some other Python IDE. If you are running from the command line simply enter the following:
 ```bash
 python bot.py
 ```

##### Running with Docker (Windows + Docker Toolbox)
If you wish to install and run the slackbot using DockerToolbox on Windows, use the following steps:

1. From the command prompt or terminal run the following inside the slython-api directory:
```bash
pip install -r requirements.txt
```
2. Then, from the terminal, run the following:
```bash
docker build -t slackbot . #this should only be done the frist time around, and then only if any changes have been made to the source code.
docker run slackbot
```
3. If you want to stop the docker image, enter the following:
```bash
docker ps
```
Note down the container id (usually a string of chars and numbers)
```
docker stop <container-id>
```

##### Running with Docker (Linux Centos)
If you wish to install and run the slackbot using Linux Centos, use the following steps:

1. From the command prompt or terminal run the following inside the slython-api directory:
```bash
sudo pip install -r requirements.txt
```
2. Then, from the terminal, run the following:
```bash
sudo service docker start
sudo docker build -t slackbot . #this should only be done the frist time around, and then only if any changes have been made to the source code.
sudo docker run slackbot
```
3. If you want to stop the docker image, you can either give the Ctrl-C command or open a new terminal window and do the following:
```bash
sudo service docker stop
```

## Usage

Below you will find a basic setup of a bot. Everything contained in that code is necessary for a slackbot instance
to run. Once the bot connects to the rtm stream, it is configured to listen to any commands you may give to it.
Of course, you can add more configurations to make your bot do anything you want.

``` python
from BotConnection import BotController as controller

# reads the json data stream and handles events
def event_handler(data_, res_):
    // handle events

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

```


Below, we have a fuller example, showing how custom integrations can be added to the slackbot using an event handler. Here
we show an example of how the slackbot can alert a channel when another channel is created. Moreover, it can also
let us know whether or not the user who created the channel is a Fitch member:

```python
from BotConnection import BotController as controller

# - - - - - - - - - - - - - - - - - - - - - - - CUSTOM METHODS - - - - - - - - - - - - - - - - - - - - - - - #

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
```



##### Methods
- ```get_connection_stream()```: connects the bot to the RTM api
- ```message_builder(title, summary, author)```: Takes three strings (the title of the message, the summary, and the author)
and returns a json dump.
- ```post_simple_message(channel_name, message)```: Takes the channel name (as a string) and the message string to be sent
and posts the message on the desired channel.
- ```get_channel(channelid)```: Takes the channel id and returns the channel json object.
- ```get_user_obj(userid)```: Takes the user id and returns the json body of the user json object.
- ```get_user_real_name(userid)```: Takes the user id and returns the real full name of the user as a string.
- ```get_file_obj(fileid)```: Takes the file id and returns the file json object.
- ```on_channel_created(data)```: Takes the RTM json stream data and returns channel json object
- ```on_file_shared(data)```: Takes the RTM json stream and returns file json object
- ```post_message_from_listener(event_type, data)```: Takes in the type of event
(channel created, user created, etc) and the corresponding json data and posts message about event.
- ```command_handler(data)```: Takes RTM JSON stream data and carries out command specified.
