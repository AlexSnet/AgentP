import logging

from tornado.ioloop import IOLoop, PeriodicCallback


def to_mseconds(td):
    if isinstance(td, int):
        return td * 1000.
    else:
        return td.total_seconds() * 1000.


class Agent(object):
    def __init__(self, name, io_loop=None, **kwargs):
        self.io_loop = io_loop or IOLoop.current()

        self.name = name
        self.prefix = kwargs.pop('prefix', getattr(self, 'PREFIX', ''))
        self.excludes = kwargs.pop('excludes', getattr(self, 'EXCLUDES', []))

        self.delay = to_mseconds(kwargs.pop('delay'))
        self.timeout = to_mseconds(kwargs.pop('timeout'))

        self.config = kwargs

        self.logger = logging.getLogger(self.name)

        self.timer = PeriodicCallback(self.run, self.delay, self.io_loop)
        self.timer.start()

    def stop(self):
        self.timer.stop()

    def run(self):
        # @TODO: Timeout handling
        self.tick()

    def gauge(self, name, value):
        if name in self.excludes:
            return

        if isinstance(value, dict):
            for k, v in value.items():
                self.gauge('%s.%s' % (name, k), v)
            return

        if self.prefix:
            name = '%s.%s' % (self.prefix, name)

        self.logger.info("%s :: %r", name, value)
