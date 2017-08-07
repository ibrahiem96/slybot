# Getting Started with Slython Slackbot API
&nbsp;&nbsp; Slython is a slackbot that builds upon the slacker python library to connect a bot to a slack team. It also connects with the RTM API to get real time events and report on those events.

##### What works in this version
&nbsp;&nbsp; As of right now Slython has the following functionality:
1. Connects to rtm and subscribes to any and all events that transpire on your slack team.
2. The API actively acknowledges and sends a message to #bot_testing_arena everytime a channel is created.
3. Reports if a channel is created and if channel creator is a fitch user
4. Reports if a file uploaded is greater than 25MB
5. Can run from a docker file
6. Integrated with Webhook URL to provide pretty-formatted JSON messages in channels.

##### Goals for the future
1. Add handler for when rtm disconnects (to automatically reconnect)
2. Determine if slack notifications/settings are accessible by bot; if so, subscribe to and interact with notification
3. Command handler (allows direct interaction with the bot from the user. i.e. if a user were to say "get me a list of all active users", the bot would then comply)
4. Write client code with wrapper functions
5. Setup EC2 Instance from which to run the dockerfile


## Setup
##### Requirements
1. Python 2.7

##### Configuration
1. Clone the repo and go inside the slython-api directory
2. In **settings.py** replace the value for API_TOKEN with the value for your bot token. If you need help creating a bot and its token, [use this guide](https://imperiallabs.github.io/quick_landing.html#get-a-key).
3. Replace the value for WEB_HOOK with your slackbot webhook url (this is also in **settings.py**). If you need assistance
   in setting up an incoming webhook URL, [go here]( https://slack.com/apps/manage/custom-integrations), and click on the incoming webhooks option.
4. Add in any other channels you with to communicate with, as done below (also in **settings.py**):
```python
    class ChannelsToPostTo:
    def __init__(self):
        self.bot_testing_arena = '#bot_testing_arena'
        self.testing_channel54 = '#testingchannel54'
```
##### Running Locally (without Docker)

1. Once setup is configured click run if you are using PyCharm or some other Python IDE. If you are running from the command line simply enter the following:
 ```bash
 python RTMConnection.py
 ```

##### Running with Docker (Windows + Docker Toolbox)
If you wish to install and run the slackbot using DockerToolbox on Windows, use the following steps:

1. From the command prompt or terminal run the following inside the slython-api directory:
```bash
pip install -r requirements.txt
```
2. Then, from the terminal, run the following:
```bash
sudo docker build -t slackbot . #this should only be done the frist time around. If you want to start the bot again, you do not need to enter this command
sudo docker run slackbot
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
2. Then, from the terminal, run the following **(NOTE: If you are using the docker quickstart terminal then you dont need to enter the first command)**:
```bash
sudo service docker start
sudo docker build -t slackbot . #this should only be done the frist time around. If you want to start the bot again, you do not need to enter this command
sudo docker run slackbot
```
3. If you want to stop the docker image, you can either give the Ctrl-C command or open a new terminal window and do the following:
```bash
sudo service docker stop
```

## Usage
#### Event Handling
Create an action for the slackbot to listen to. In this case, we will listen to the rtm api to see when a channel
is created and then check if that channel was created by a Fitch user **(Notice that we use the on_channel_created() method here)**:
```python
# gets user info based on user ID
def report_if_fitch_user(data):

    channel_obj = on_channel_created(data)
    user_obj = get_user_obj(channel_obj['channel']['creator'])

    if 'fitchratings' in user_obj['user']['profile']['email']:
        post_message_from_listener('channel created', channel_obj)
        post_simple_message('#bot_testing_arena', 'Channel Created By Fitch User')
        post_simple_message('#bot_testing_arena', 'User Email: ' + user_obj['user']['profile']['email'])
```

Then we make sure that this method is being called in our event_handler method:
```python
# reads the json data stream and handles events
def event_handler(data_, res_):
    # alerts channel if another channel is created
    if "channel_created" in res_:
        report_if_fitch_user(data_)
```

The event handler is set to run always so you do not need to worry about that.

#### Simple Actions
If you want to complete a simple action such as posting a message, without involving the event handler, you can
do this as well, by doing that anywhere before the RTM loop.

##### Methods
###### Immutable
- ```message_builder(title, summary, author)```: Takes three strings (the title of the message, the summary, and the author)
and returns a json object.
- ```event_handler(data_, res_)```: Takes in json rtm stream and data runs handler methods. This method is only
and should only be run in the MAIN RTM LOOP.
###### Mutable
- ```post_simple_message(channel_name, message)```: Takes the channel name (as a string) and the message string to be sent
and posts the message on the desired channel.
- ```get_channel(channelid)```: Takes the channel id and returns the channel json object.
- ```get_user_obj(userid)```: Takes the user id and returns the json body of the user json object.
- ```get_user_real_name(userid)```: Takes the user id and returns the real full name of the user as a string.
- ```get_file_obj(fileid)```: Takes the file id and returns the file json object.
- ```on_channel_created(data)```: Takes the RTM json stream data and returns channel json object
- ```post_message_from_listener(event_type, data)```: Takes in the type of event
(channel created, user created, etc) and the corresponding json data and posts message about event.




 
