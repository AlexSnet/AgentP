"""
Agent P(erry)
"""

import logging
import importlib

from configure import Configuration

from tornado.options import parse_command_line
from tornado.options import define, options


class AgentP(object):
    config = None

    def __init__(self):
        self._modules = {}
        self._agents = {}

    def run_command_line(self):
        define("configuration", default="/etc/agentp/agent.conf", help="Configuration file")
        parse_command_line()

        try:
            self.config = Configuration.from_file(options.configuration).configure()
            logging.info('Reading configuration from %s', options.configuration)
        except IOError:
            print('Configuration file "%s" does not exists.' % options.configuration)
            raise SystemExit(1)

        for agent in self.config.agents:
            if isinstance(agent, str):
                self.configure_agent(agent)
            elif isinstance(agent, dict) and 'module' in agent:
                self.configure_agent(agent.pop('module'), **agent)

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
        mod = self.get_module(module)
        logging.info('Module "%s" is %r', module, mod)

