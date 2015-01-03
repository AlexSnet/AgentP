from __future__ import absolute_import

import redis
from agentp import Agent


class Redis(Agent):
    EXCLUDES = (
        'used_memory_peak_human',
        'redis_build_id',
        'run_id',
        'redis_mode',
        'multiplexing_api',
        'redis_version',
        'gcc_version',
        'rdb_current_bgsave_time_sec',
        'rdb_last_save_time',
        'role',
        'sync_full',
        'config_file',
        'rdb_last_bgsave_status',
        'aof_last_bgrewrite_status',
        'used_memory_human',
        'process_id',
        'os',
        'aof_rewrite_scheduled'
        'aof_enabled',
        'mem_allocator',
        'aof_current_rewrite_time_sec',
        'arch_bits',
        'repl_backlog_active',
        'rdb_last_bgsave_time_sec',
        'rdb_bgsave_in_progress',
        'rdb_changes_since_last_save',
        'master_repl_offset',
        'tcp_port',
        'sync_partial_ok',
        'redis_git_sha1',
        'lru_clock',
        'uptime_in_days',
        'aof_rewrite_in_progress',
        'redis_git_dirty',
    )

    def tick(self):
        r = redis.StrictRedis.from_url(self.config.get('dsl', 'redis://localhost:6379/0'))

        info = r.info()
        for i in info.items():
            self.gauge(i[0], i[1])

        for q in self.config.get('queues', []):
            self.gauge("queue." % q, r.llen(q))
