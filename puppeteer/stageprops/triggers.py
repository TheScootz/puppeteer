from ..stageprops import *

@on('001')
@triggers('rpl_welcome')
def rpl_welcome(*args):
    return True

@on('376')
@triggers('rpl_endofmotd')
def rpl_endofmotd(*args):
    return True

@on('422')
@triggers('err_nomotd')
def err_nomotd(*args):
    return True

@on('join')
@triggers('my_join')
def my_join(puppet, source, channel):
    if source.split("!")[0] == puppet.nickname:
        return True

@on('join')
@triggers('other_join')
def other_join(puppet, source, channel):
    if source.split("!")[0] != puppet.nickname:
        return True

@on('part')
@triggers('my_part')
def my_part(puppet, source, channel):
    if source.split("!")[0] == puppet.nickname:
        return True

@on('part')
@triggers('other_part')
def other_part(puppet, source, channel):
    if source.split("!")[0] != puppet.nickname:
        return True
