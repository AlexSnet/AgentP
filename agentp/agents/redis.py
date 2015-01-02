import redis

from agentp import Agent


class Redis(Agent):
    def tick(self):
        r = redis.StrictRedis.from_url(self.config.get('dsl', 'redis://localhost:6379/0'))

        info = r.info()
        print('Redis INFO:', info)
        for q in self.config.get('queues', []):
            r.llen(q)