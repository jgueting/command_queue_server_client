from comqueue.server import Server
import logging
logging.basicConfig(level=logging.INFO)

class TestServer(Server):
    def greet(self, data):
        msg = str(data[0])
        self.err_queue.put(msg)
        logging.info(msg)



if __name__ == '__main__':
    import os
    server = TestServer(os.path.join(os.getcwd(), 'comqueue', 'config.json'))

    server.run()