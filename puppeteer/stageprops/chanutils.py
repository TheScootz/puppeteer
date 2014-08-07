import timeit

from puppeteer.stageprops import *

@on(command='privmsg', \
    to_channel=True, \
    text="@ping")
def pong_request(puppet, source, target, message):
    puppet.protocol.put('privmsg', target, "Pong!")

@on(command='privmsg', \
    to_channel=True, \
    text="@rehash", \
    username=puppeteer.config['stageprops']['chanutils']['admin']['username'], \
    hostname=puppeteer.config['stageprops']['chanutils']['admin']['hostname']) # hack for now
def rehash_request(puppet, source, target, message):
    start = timeit.default_timer()
    puppeteer.rehash()
    elapsed = (timeit.default_timer() - start) * 1000
    puppet.protocol.put('privmsg', target, "Rehashed ({:.4}ms)".format(elapsed))
