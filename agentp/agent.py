import time
import logging

from tornado.ioloop import IOLoop, PeriodicCallback


class Agent(object):
    def __init__(self, name, io_loop=None, **kwargs):
        self.io_loop = io_loop or IOLoop.current()

        self.name = name

        self.delay = kwargs.pop('delay')
        self.timeout = kwargs.pop('timeout')

        self.config = kwargs

        self.logger = logging.getLogger(self.name)

        self.timer = PeriodicCallback(self.run, self.timeout, self.io_loop)
        self.timerm.start()

    def stop(self):
        self.timer.stop()

    def run(self):
        self.tick()

    def gauge(self, name, value):
        self.logger.info("%s :: %r", name, value)
