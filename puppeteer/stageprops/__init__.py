import asyncio
from functools import wraps

handlers = []

def handle(event_name, *args, **kwargs):
    for _, handler_event_name, _, handler in handlers:
        if event_name == handler_event_name:
            handler(*args, **kwargs)

def on(event_name, priority=20):
    def decorator(handler):
        handler_name = "{}.{}".format(handler.__module__.split(".")[-1], handler.__qualname__)
        handlers.append((priority, event_name, handler_name, handler))

        @wraps(handler)
        def wrapper(*args, **kwargs):
            handler(*args, **kwargs)
        return wrapper

    return decorator

def triggers(event_name):
    def decorator(check):
        
        @wraps(check)
        def wrapper(*args, **kwargs):
            if check(*args, **kwargs):
                handle(event_name, *args, **kwargs)
        return wrapper
    
    return decorator

__all__ = ['on', 'triggers', 'puppeteer']
