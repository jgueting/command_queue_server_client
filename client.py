from multiprocessing.managers import BaseManager
import json, os


class Client:
    class CommandManager(BaseManager): pass
    class ErrorManager(BaseManager): pass

    def __init__(self):
        self.name = self.__class__.__name__
        ### initialize remote command system

        # load config
        with open(os.path.join(os.getcwd(), 'config.json'), 'r') as configfile:
            self.config = json.load(configfile)['control']

        # initialize command transmitter queue
        Client.CommandManager.register('get_queue')
        self.com_qm = Client.CommandManager(address=(self.config['command queue']['address'][0], self.config['command queue']['port']),
                                            authkey=self.config['command queue']['authkey'].encode('ascii'))

        # initialize (error-)report receiver queue
        Client.ErrorManager.register('get_queue')
        self.err_qm = Client.ErrorManager(address=(self.config['error queue']['address'][0], self.config['error queue']['port']),
                                          authkey=self.config['error queue']['authkey'].encode('ascii'))

        self._connect()

    def _connect(self, *args):
        self.com_qm.connect()
        self.com_queue = self.com_qm.get_queue()

        self.err_qm.connect()
        self.err_queue = self.err_qm.get_queue()

