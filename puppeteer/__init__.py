import asyncio
import heapq
import importlib
import puppeteer.stageprops as stageprops
import random
import re

MESSAGE_REGEX = re.compile("(?::([^ ]*) )?([^ :]+)(?: ([^ :]+))*(?: :(.*))?\r\n")
SOURCE_REGEX = re.compile("(?:([^!]*)!)?(?:([^@]*)@)?(.*)?")
REPLY_REGEX = re.compile('[0-9]{3}')

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
            self.loop.stop()
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
            stageprops.stageprops[prop_name] = heapsort(stageprops.stageprops[prop_name])

        for prop_name in self.config['stageprops']:
            if prop_name in self.loaded_props:
                continue
            print("Loading {}.stageprops.{}...".format(__package__, prop_name))
            prop = importlib.import_module("{}.stageprops.{}".format(__package__, prop_name))
            self.loaded_props[prop_name] = prop
            stageprops.stageprops[prop_name] = heapsort(stageprops.stageprops[prop_name])
            
    def set_up_props(self):
        stageprops.puppeteer = self
        self.rehash()

class Puppet:
    def __init__(self, puppeteer, config):
        self.puppeteer = puppeteer
        self.config = config
        self.protocol = None

    def start_timers(self):
        for i, timer in enumerate(stageprops.timers):
            print("Starting timer {}...".format(i))
            timer(self)

    def on_connect(self, future):
        _, self.protocol = future.result()
        self.protocol.bot = self
        
        nickname = self.config['nickname'][0]
        while nickname.count("?"):
            nickname = nickname.replace("?", str(random.randint(0,9)), 1)

        username = self.config['username']
        while username.count("?"):
            username = username.replace("?", str(random.randint(0,9)), 1)
        
        self.protocol.put('nick', nickname)
        self.protocol.put('user', username, self.config['realname'])

    def handle_event(self, source, command, params):
        event_details = {}

        # This sequence of adding details should be separated and improved later

        if source is not None:
            event_details['nickname'], \
                event_details['username'], \
                event_details['hostname'] = re.match(SOURCE_REGEX, source).groups()
        else:
            event_details['nickname'], \
                event_details['username'], \
            event_details['hostname'] = (None, None, None)

        if re.match(REPLY_REGEX, command):
            event_details['reply'] = command
        else:
            event_details['command'] = command
            if command == 'privmsg':
                event_details['target'] = params[0]
                event_details['text'] = params[1]
                if event_details['target'][0] in "#&!+":
                    event_details['to_channel'] = True
                    event_details['channel'] = event_details['target']
                else:
                    event_details['to_channel'] = False

        for prop in self.config['stageprops']:
            for _, event_handler in stageprops.stageprops[prop]:
                if set(event_handler.requirements.items()) == \
                   set(event_handler.requirements.items()) & set(event_details.items()):
                    event_handler.function(self, source, *params)
                
    def enter(self):
        print("[Enter {}]".format(self.alias))
        task = asyncio.async(self.puppeteer.loop.create_connection(
            IRCClient, self.config['host'], self.config['port']))
        task.add_done_callback(self.on_connect)
        self.start_timers()
