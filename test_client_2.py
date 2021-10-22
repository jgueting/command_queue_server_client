from comqueue.client import Client


if __name__ == '__main__':
    from time import sleep
    import os

    client = Client(os.path.join(os.getcwd(), 'comqueue', 'config.json'))

    try:
        while True:
            client.send('greet', ['hallo from 2'])
            sleep(1.01)
    except KeyboardInterrupt:
        client.send('shutdown', [])
