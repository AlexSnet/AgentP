import time
import logging

from tornado.ioloop import IOLoop


class Agent(object):
    def __init__(self, name, io_loop=None, **kwargs):
        self.io_loop = io_loop or IOLoop.current()

        self.name = name
        self.config = kwargs

        self.logger = logging.getLogger(self.name)

    def run(self):
        while True:
            self.tick()
            time.sleep(4)

    def gauge(self, name, value):
        self.logger.info("%s :: %r", name, value)
