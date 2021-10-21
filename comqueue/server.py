from multiprocessing import Queue
from multiprocessing.managers import BaseManager
from time import time, sleep
import logging
import json


class Server:
    class CommandManager(BaseManager):
        pass

    class ErrorManager(BaseManager):
        pass

    def __init__(self, configfilename):
        self.name = self.__class__.__name__
        logging.info(f'*** {self.name} ***')

        try:
            # load config ###########################
            with open(configfilename, 'r') as configfile:
                self.config = json.load(configfile)['control']

            # initialize remote command system ######

            # initialize command receiver queue
            self.com_queue = Queue(maxsize=self.config['command queue']['maxsize'])
            Server.CommandManager.register('get_queue', callable=lambda : self.com_queue)
            self.com_qm = Server.CommandManager(address=('', self.config['command queue']['port']),
                                                authkey=self.config['command queue']['authkey'].encode('ascii'))
            self.com_qm.start()

            # initialize (error-)report transmitter queue
            self.err_queue = Queue()
            Server.ErrorManager.register('get_queue', callable=lambda : self.err_queue)
            self.err_qm = Server.ErrorManager(address=('', self.config['error queue']['port']),
                                              authkey=self.config['error queue']['authkey'].encode('ascii'))
            self.err_qm.start()

            # init timing ###########################
            self.loop_time = self.config['loop time']
            self.calc_time_avg = 0.
            self.calc_time_max = 0.

            msg = f'{self.name}: Remote Command System initialized.'
            logging.info(msg)
            self.err_queue.put(msg)
        except Exception as err:
            logging.error(f'{type(err).__name__}: {err}', exc_info=True)

    def run(self):
        starttime = time()
        command = ''
        inc = 0
        avg_value = 100
        time_list = [0. for i in range(avg_value)]

        while not command == 'shutdown':
            # do what needs to be done
            self.work()

            # handle commands
            while not self.com_queue.empty():
                try:
                    command, data = self.com_queue.get()
                except Exception as err:
                    logging.error(f'{self.name}: {type(err).__name__}: {err}', exc_info=True)
                else:
                    if hasattr(self, command):
                        try:
                            getattr(self, command)(data)
                        except Exception as err:
                            err_string = f'{self.name} ({command}, {data}): {type(err).__name__}: {err}'
                            logging.error(err_string, exc_info=True)
                            self.err_queue.put(err_string)
                    else:
                        err_string = 'CommandError: command not found: {}'.format(command)
                        logging.info(err_string)
                        self.err_queue.put(err_string)

            # control loop time
            if not command == 'shutdown':
                try:
                    now = time()
                    wait_time = self.loop_time - (now - starttime - inc * self.loop_time)
                    time_list = time_list[1:] + [self.loop_time - wait_time]
                    self.calc_time_avg = sum(time_list) / avg_value
                    self.calc_time_max = max(time_list)
                    sleep(wait_time)
                except Exception:
                    out = f'{self.name}: loop time warning: {(self.loop_time - wait_time) * 1000:5.3f}ms > ' \
                          f'{self.loop_time * 1000:5.3f}ms)'
                    logging.warning(out)
                    starttime = now
                    inc = 0
            inc += 1

    def work(self):
        pass

    # shutdown command method (create other commands in the same pattern!)
    def shutdown(self, data):
        message = f'{self.name}: shutting down ...'
        logging.info(message)
        self.err_queue.put(message)

    def __del__(self):
        start_time = time()
        while not self.err_queue.empty() and time() - start_time < 2:
            pass
        self.err_qm.shutdown()
        self.com_qm.shutdown()
        logging.info(f'{self.name}: terminated.')
