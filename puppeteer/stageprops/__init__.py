import asyncio
from functools import wraps

stageprops = {}
timers = []

class EventHandler:
    def __init__(self, function, requirements):
        self.function = function
        self.requirements = requirements

    def __lt__(self, *args):
        return True

def on(priority=20, **requirements):
    def decorator(f):
        prop_name = f.__module__.split(".")[-1]

        if prop_name not in stageprops:
            stageprops[prop_name] = []

        stageprops[prop_name].append((priority, EventHandler(f, requirements)))

        @wraps(f)
        def wrapper(*args, **kwargs):
            f(*args, **kwargs)
        return wrapper

    return decorator

def timer(interval=None):
    def decorator(f):
        @wraps(f)
        def timer_wrapper(*args, **kwargs):
            f(*args, **kwargs)
            asyncio.get_event_loop().call_later(interval, timer_wrapper, *args, **kwargs)
        timers.append(timer_wrapper)

        @wraps(f)
        def wrapper(*args, **kwargs):
            f(*args, **kwargs)
        return wrapper
    return decorator

__all__ = ['on', 'timer', 'puppeteer']
