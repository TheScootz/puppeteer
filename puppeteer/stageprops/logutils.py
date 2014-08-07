from puppeteer.stageprops import *

@on(reply='001')
def log_connected(puppet, *args):
    print('{}: Connected!'.format(puppet.alias))

@on(command='join')
def log_joined_channel(puppet, source, channel):
    if source.split("!")[0] == puppet.nickname:
        print('{}: Joined {}!'.format(puppet.alias, channel))
