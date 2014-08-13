from ..stageprops import *

@on('ping')
def send_pong(puppet, source, server):
    puppet.protocol.put('pong', server)

@on('rpl_endofmotd')
@on('err_nomotd')
def autojoin_config_channels(puppet, source, target, text):
    puppet.protocol.put('join', ",".join(puppet.config['channels']))

@on('rpl_welcome')
def detect_connected(puppet, source, nickname, message):
    puppet.nickname = nickname


