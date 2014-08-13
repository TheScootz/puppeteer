import asyncio
import heapq
import importlib
import puppeteer.stageprops as stageprops
import puppeteer.util as util
import re

MESSAGE_REGEX = re.compile("(?::([^ ]*) )?([^ :]+)(?: ([^ :]+))*(?: :(.*))?\r\n")
SOURCE_REGEX = re.compile("(?:([^!]*)!)?(?:([^@]*)@)?(.*)?")

class IRCClient(asyncio.Protocol):
    def __init__(self):
        self.command_map = {
            0: {
                'quit':    "QUIT",
            },
            1: {
                'join':    "JOIN {}",
                'mode':    "MODE {}",
                'nick':    "NICK {}",
                'part':    "PART {}",
                'pong':    "PONG :{}",
                'quit':    "QUIT :{}",
                'topic':   "TOPIC {}",
            },
            2: {
                'join':    "JOIN {} {}",
                'mode':    "MODE {} {}",
                'notice':  "NOTICE {} :{}",
                'part':    "PART {} :{}",
                'privmsg': "PRIVMSG {} :{}",
                'topic':   "TOPIC {} :{}",
                'user':    "USER {} 0 * :{}",
            },
            3: {
                'user':    "USER {} {} * :{}",
            },
        }

    def connection_made(self, transport):
        self.transport = transport
        self.queue = asyncio.Queue()

    def put(self, command, *params):
        message = self.command_map[len(params)][command].format(*params)
        self.put_(message)

    def put_(self, message):
        self.transport.write("{}\r\n".format(message).encode())

    def data_received(self, data):
        data = data.decode()
        try:
            data = self.queue.get_nowait() + data
        except asyncio.QueueEmpty:
            pass

        message_match = re.match(MESSAGE_REGEX, data)

        if not message_match:
            print("Error: Got invalid message from server: {}".format(data))
            return

        while message_match:
            print("<- {}".format(message_match.groups()))
            source = message_match.groups()[0]
            command = message_match.groups()[1].lower()
            params = [param for param in message_match.groups()[2:] if param is not None]

            self.bot.handle_event(source, command, params)

            data = data[message_match.end():]
            message_match = re.match(MESSAGE_REGEX, data)

        self.queue.put_nowait(data)

    def connection_lost(self, exc):
        print("Lost connection")

class Puppeteer:
    def __init__(self, config, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.puppets = {}
        self.config = config
        self.loaded_props = {}
        for puppet_alias, puppet_config in self.config['puppets'].items():
            self.puppets[puppet_alias] = Puppet(self, puppet_config)
            self.puppets[puppet_alias].alias = puppet_alias

    def perform(self):
        for puppet in self.puppets.values():
            self.loop.call_soon(puppet.enter)
        try:
            self.loop.run_forever()
        finally:
            self.loop.close()

    def rehash(self):
        def heapsort(priority_functions):
            h = []
            for function in priority_functions:
                heapq.heappush(h, function)
            return [heapq.heappop(h) for i in range(len(h))]

        importlib.reload(stageprops)

        for prop_name in self.loaded_props:
            print("Reloading {}.stageprops.{}...".format(__package__, prop_name))
            importlib.reload(self.loaded_props[prop_name])

        for prop_name in self.config['stageprops']:
            if prop_name in self.loaded_props:
                continue
            print("Loading {}.stageprops.{}...".format(__package__, prop_name))
            prop = importlib.import_module("{}.stageprops.{}".format(__package__, prop_name))
            self.loaded_props[prop_name] = prop

        stageprops.handlers = heapsort(stageprops.handlers)

    def set_up_props(self):
        stageprops.puppeteer = self
        self.rehash()

class Puppet:
    def __init__(self, puppeteer, config):
        self.puppeteer = puppeteer
        self.config = config
        self.protocol = None

    def on_connect(self, future):
        _, self.protocol = future.result()
        self.protocol.bot = self
        
        self.nickname = util.convert_qmarks(self.config['nickname'][0])
        self.username = util.convert_qmarks(self.config['username'])
        self.realname = self.config['realname']
        
        self.protocol.put('nick', self.nickname)
        self.protocol.put('user', self.username, self.realname)

    def handle_event(self, source, message_type, params):
        stageprops.handle(message_type, self, source, *params)
                
    def enter(self):
        print("[Enter {}]".format(self.alias))
        task = asyncio.async(self.puppeteer.loop.create_connection(
            IRCClient, self.config['host'], self.config['port']))
        task.add_done_callback(self.on_connect)
