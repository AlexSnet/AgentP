import psutil
from agentp import Agent
from agentp.platforms import Platform


class DiskUsage(Agent):
    def tick(self):
        # c = statsd.StatsClient('localhost', 8125, prefix='system.disk')
        disk_usage = psutil.disk_usage(self.config.get('path', '/'))
        self.gauge('root.total', disk_usage.total)
        self.gauge('root.used', disk_usage.used)
        self.gauge('root.free', disk_usage.free)
        self.gauge('root.percent', disk_usage.percent)


class CPUTimes(Agent):
    def tick(self):
        # c = statsd.StatsClient('localhost', 8125, prefix='system.cpu')
        cpu_times = psutil.cpu_times()
        self.gauge('system_wide.times.user', cpu_times.user)
        self.gauge('system_wide.times.nice', cpu_times.nice)
        self.gauge('system_wide.times.system', cpu_times.system)
        self.gauge('system_wide.times.idle', cpu_times.idle)
        self.gauge('system_wide.times.iowait', cpu_times.iowait)
        self.gauge('system_wide.times.irq', cpu_times.irq)
        self.gauge('system_wide.times.softirq', cpu_times.softirq)
        self.gauge('system_wide.times.steal', cpu_times.steal)
        self.gauge('system_wide.times.guest', cpu_times.guest)
        self.gauge('system_wide.times.guest_nice', cpu_times.guest_nice)


class CPUTimesPercent(Agent):
    def tick(self):
        # c = statsd.StatsClient('localhost', 8125, prefix='system.cpu')
        value = psutil.cpu_percent(interval=1)
        self.gauge('system_wide.percent', value)

        cpu_times_percent = psutil.cpu_times_percent(interval=1)
        self.gauge('system_wide.times_percent.user', cpu_times_percent.user)
        self.gauge('system_wide.times_percent.nice', cpu_times_percent.nice)
        self.gauge('system_wide.times_percent.system', cpu_times_percent.system)
        self.gauge('system_wide.times_percent.idle', cpu_times_percent.idle)
        self.gauge('system_wide.times_percent.iowait', cpu_times_percent.iowait)
        self.gauge('system_wide.times_percent.irq', cpu_times_percent.irq)
        self.gauge('system_wide.times_percent.softirq', cpu_times_percent.softirq)
        self.gauge('system_wide.times_percent.steal', cpu_times_percent.steal)
        self.gauge('system_wide.times_percent.guest', cpu_times_percent.guest)
        self.gauge('system_wide.times_percent.guest_nice', cpu_times_percent.guest_nice)


class Memory(Agent):
    def tick(self):
        # c = statsd.StatsClient('localhost', 8125, prefix='system.memory')
        swap = psutil.swap_memory()
        self.gauge('swap.total', swap.total)
        self.gauge('swap.used', swap.used)
        self.gauge('swap.free', swap.free)
        self.gauge('swap.percent', swap.percent)

        virtual = psutil.virtual_memory()
        self.gauge('virtual.total', virtual.total)
        self.gauge('virtual.available', virtual.available)
        self.gauge('virtual.used', virtual.used)
        self.gauge('virtual.free', virtual.free)
        self.gauge('virtual.percent', virtual.percent)
        self.gauge('virtual.active', virtual.active)
        self.gauge('virtual.inactive', virtual.inactive)
        self.gauge('virtual.buffers', virtual.buffers)
        self.gauge('virtual.cached', virtual.cached)
