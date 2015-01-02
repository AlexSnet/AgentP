import os
import pwd
import glob
import platform

from collections import OrderedDict, namedtuple

from agentp.platforms.base import PlatformBase


class Linux(PlatformBase):
    def cpuinfo(self):
        ''' Return the information in /proc/cpuinfo
        as a dictionary in the following format:
        cpu_info['proc0']={...}
        cpu_info['proc1']={...}

        '''

        cpuinfo = OrderedDict()
        procinfo = OrderedDict()

        nprocs = 0
        with open('/proc/cpuinfo') as f:
            for line in f:
                if not line.strip():
                    # end of one processor
                    cpuinfo['proc%s' % nprocs] = procinfo
                    nprocs = nprocs+1
                    # Reset
                    procinfo = OrderedDict()
                else:
                    if len(line.split(':')) == 2:
                        procinfo[line.split(':')[0].strip()] = line.split(':')[1].strip()
                    else:
                        procinfo[line.split(':')[0].strip()] = ''

        return cpuinfo

    def meminfo(self):
        ''' Return the information in /proc/meminfo
        as a dictionary '''
        meminfo = OrderedDict()

        with open('/proc/meminfo') as f:
            for line in f:
                meminfo[line.split(':')[0]] = line.split(':')[1].strip()
        return meminfo

    def netdevs(self):
        ''' RX and TX bytes for each of the network devices '''

        with open('/proc/net/dev') as f:
            net_dump = f.readlines()

        device_data = {}
        data = namedtuple('data', ['rx', 'tx'])
        for line in net_dump[2:]:
            line = line.split(':')
            if line[0].strip() != 'lo':
                device_data[line[0].strip()] = \
                    data(float(line[1].split()[0])/(1024.0*1024.0),
                         float(line[1].split()[8])/(1024.0*1024.0))

        return device_data

    def process_list(self):
        pids = []
        for subdir in os.listdir('/proc'):
            if subdir.isdigit():
                pids.append(subdir)

        return pids

    def read_login_defs(self):
        uid_min = None
        uid_max = None

        if os.path.exists('/etc/login.defs'):
            with open('/etc/login.defs') as f:
                login_data = f.readlines()

            for line in login_data:
                if line.startswith('UID_MIN'):
                    uid_min = int(line.split()[1].strip())

                if line.startswith('UID_MAX'):
                    uid_max = int(line.split()[1].strip())

        return uid_min, uid_max

    # Get the users from /etc/passwd
    def getusers(self, no_system=False):
        uid_min, uid_max = self.read_login_defs()

        if uid_min is None:
            uid_min = 1000
        if uid_max is None:
            uid_max = 60000

        users = pwd.getpwall()
        for user in users:
            if no_system:
                if user.pw_uid >= uid_min and user.pw_uid <= uid_max:
                    print('{0}:{1}'.format(user.pw_name, user.pw_shell))
            else:
                print('{0}:{1}'.format(user.pw_name, user.pw_shell))
