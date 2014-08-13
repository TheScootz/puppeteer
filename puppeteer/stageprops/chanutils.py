import timeit

from ..stageprops import *

@on('privmsg')
def handle_pong_request(puppet, source, target, message):
    if message != "@ping":
        return

    nickname = source.split("!")[0]

    if target[0] in "#&":
        puppet.protocol.put('privmsg', target, "{}: Pong!".format(nickname))
    else:
        puppet.protocol.put('privmsg', nickname, "Pong!")

@on('privmsg')
def handle_rehash_request(puppet, source, target, message):
    if message != "@rehash":
        return

    start = timeit.default_timer()
    puppeteer.rehash()
    elapsed = (timeit.default_timer() - start) * 1000

    nickname = source.split("!")[0]

    if target[0] in "#&":
        puppet.protocol.put('privmsg', target, "{}: Rehashed ({:.4}ms)".format(nickname, elapsed))
    else:
        puppet.protocol.put('privmsg', nickname, "Rehashed ({:.4}ms)".format(elapsed))
