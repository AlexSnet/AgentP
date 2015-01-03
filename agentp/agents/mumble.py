import os
import sys
import logging
import tempfile

from agentp.agent import Agent

try:
    import Ice
    import IcePy
except ImportError:
    logging.error('Can not use mumble agent without installed zeroc-ice python package.')
    raise SystemExit(1)


class Mumble(Agent):
    def __init__(self, **kwargs):
        logging.info('Mumble agent loaded')

        self.host = kwargs.get('host', '127.0.0.1')
        self.port = int(kwargs.get('port', 6502))
        self.secret = kwargs.get('secret', '')

        self.slice_file = kwargs.get('slicefile', 'Mumble.ice')

        self.configure_ice()
        self.configure_slice()
        self.configure_connection()
        self.get_booted_servers()

    def configure_ice(self):
        logging.info('Configuring Ice connector.')

        prxstr = "Meta:tcp -h %s -p %d -t 1000" % (self.host, self.port)

        props = Ice.createProperties()
        props.setProperty("Ice.ImplicitContext", "Shared")
        idata = Ice.InitializationData()
        idata.properties = props

        self.ice = Ice.initialize(idata)
        self.prx = self.ice.stringToProxy(prxstr)

        logging.info('Ice connector configured')

    def configure_slice(self):
        logging.info('Configuring Ice slice.')

        slicedir = Ice.getSliceDir()
        if not slicedir:
            slicedir = ["-I/usr/share/Ice/slice", "-I/usr/share/slice"]
        else:
            slicedir = ['-I' + slicedir]

        try:
            logging.info('Trying to retrieve slice dynamically from server...')
            op = None
            if IcePy.intVersion() < 30500L:
                # Old 3.4 signature with 9 parameters
                op = IcePy.Operation('getSlice', Ice.OperationMode.Idempotent, Ice.OperationMode.Idempotent, True, (), (), (), IcePy._t_string, ())
            else:
                # New 3.5 signature with 10 parameters.
                op = IcePy.Operation('getSlice', Ice.OperationMode.Idempotent, Ice.OperationMode.Idempotent, True, None, (), (), (), ((), IcePy._t_string, False, 0), ())

            slice = op.invoke(self.prx, ((), None))
            (dynslicefiledesc, dynslicefilepath) = tempfile.mkstemp(suffix='.ice')
            dynslicefile = os.fdopen(dynslicefiledesc, 'w')
            dynslicefile.write(slice)
            dynslicefile.flush()
            Ice.loadSlice('', slicedir + [dynslicefilepath])
            dynslicefile.close()
            os.remove(dynslicefilepath)

        except Exception:
            logging.error('Can not retrieve slice from server...')
            raise SystemExit(1)

    def configure_connection(self):
        logging.info('Configuring connection')
        import Murmur
        self.mm = Murmur
        if self.secret:
            self.ice.getImplicitContext().put("secret", self.secret)
        self.murmur = Murmur.MetaPrx.checkedCast(self.prx)

    def get_booted_servers(self):
        logging.info('Retrieving booted servers')
        try:
            self.booted_servers = self.murmur.getBootedServers()
        except self.mm.InvalidSecretException:
            logging.error('Invalid ice secret.')
