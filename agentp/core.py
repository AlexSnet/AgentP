"""
Agent P(erry)
"""

import time
import signal
import logging
import importlib

from datetime import timedelta

from agentp.configure import Configuration

from tornado.options import parse_command_line
from tornado.options import define, options
from tornado.ioloop import IOLoop
from tornado import process


class AgentP(object):
    config = None

    def __init__(self):
        self._modules = {}
        self._agents = {}
        self._backends = {}

        self.io_loop = None

    def signal_cb(self, handle, signum):
        logging.info('Signal received: %r, %r', handle, signum)
        IOLoop.instance().add_callback_from_signal(lambda: IOLoop.current().stop())

    def run_command_line(self):
        define("configuration", default="/etc/agentp/agent.conf", help="Configuration file")
        parse_command_line()

        # Register signal handler
        signal.signal(signal.SIGUSR1, self.signal_cb)
        signal.signal(signal.SIGUSR2, self.signal_cb)
        signal.signal(signal.SIGHUP, self.signal_cb)
        signal.signal(signal.SIGINT, self.signal_cb)

        # Reading configuration
        try:
            self.config = Configuration.from_file(options.configuration).configure()
            logging.info('Reading configuration from %s', options.configuration)
        except IOError:
            print('Configuration file "%s" does not exists.' % options.configuration)
            raise SystemExit(1)

        default_config = {
            'delay': timedelta(seconds=10),
            'timeout': timedelta(seconds=60)
        }

        default_config.update({
            'delay': self.config.get('delay', default_config['delay']),
            'timeout': self.config.get('timeout', default_config['timeout'])
        })

        # Forking
        workers = self.config.get('workers', None)
        if workers == 1 or workers == 'none' or not workers:
            pass
        else:
            process.fork_processes(int(workers) if workers != 'auto' else 0)

        # Defining IOLoop
        self.io_loop = IOLoop.current()

        # Configuring backends

        # Configuring agents
        if process.task_id() == 0 or not process.task_id():
            for agent in self.config.agents:
                if isinstance(agent, str):
                    self.io_loop.add_callback(self.configure_agent, agent, **default_config)
                elif isinstance(agent, dict) and 'module' in agent:
                    self.io_loop.add_callback(self.configure_agent, agent.pop('module'), **dict(default_config.items() + agent.items()))

        # Starting IOLoop
        self.io_loop.start()

    def get_module(self, module):
        if module not in self._modules:
            try:
                mod = importlib.import_module(module)
            except Exception, e:
                logging.error('Loading module "%s" failed: %s', module, e)
            except SystemExit:
                logging.error('SystemExit raised when loading module "%s".', module)
            else:
                logging.info('Module "%s" loaded', module)
                self._modules[module] = mod

        return self._modules[module] if module in self._modules else None

    def configure_agent(self, module, **kwargs):

        agent = kwargs.pop('agent') if 'agent' in kwargs else None
        if ':' in module:
            module, agent = module.split(':', 1)
        if not agent:
            agent = module.split('.')[-1].title()

        mod = self.get_module(module)

        name = kwargs.get('name', "%s:%s" % (module, agent))
        if 'name' in kwargs:
            kwargs.pop('name')

        if name in self._agents:
            logging.error('Name "%s" is already taken by "%s", use another name to use this agent.', name, self._agents[name])
            return

        agi = None
        if agent:
            if hasattr(mod, agent):
                agi = getattr(mod, agent)

        if agi:
            logging.info('Agent "%s" (%s:%s) registered.', name, module, agent)
            self._agents[name] = agi(name, **kwargs)
