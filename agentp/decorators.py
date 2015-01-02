import logging


def register_agent(namespace='', timeout=10, delay=10):
    def decorator(func):
        logging.info('Registering agent for "%s" @ %s', func.__name__, namespace or 'agent')

    return decorator
