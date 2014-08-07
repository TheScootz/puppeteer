from puppeteer.stageprops import *

@on(command='ping')
def send_pong(puppet, source, server):
    puppet.protocol.put('pong', server)

@on(reply='376')
@on(reply='422')
def autojoin_config_channels(puppet, source, target, text):
    puppet.protocol.put('join', ",".join(puppet.config['channels']))

@on(reply='001')
def detect_my_nickname(puppet, source, nickname, message):
    puppet.nickname = nickname
