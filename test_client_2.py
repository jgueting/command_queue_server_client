from comqueue.client import Client


if __name__ == '__main__':
    from time import sleep, time
    import os

    retry = 20

    start = time()

    try:
        client = Client(os.path.join(os.getcwd(), 'comqueue', 'config.json'))
    except Exception as err:
        print(f'{type(err).__name__}: {err}')
        retry = 0
    else:
        print(f'{time() - start:6.3f}ms: connection established!')

    while retry:
        try:
            while True:
                client.send('greet', ['hallo from 2'])
                sleep(1.01)
        except (EOFError, ConnectionRefusedError, ConnectionAbortedError) as err:
            print(f'{time() - start:6.3f}ms: {type(err).__name__}')
            sleep(1)
            retry -= 1
            try:
                client.connect()
            except ConnectionRefusedError as err:
                print(f'{time() - start:6.3f}ms: {type(err).__name__}')
            except Exception as err:
                print(f'{time() - start:6.3f}ms: {type(err).__name__}: {err}')
            else:
                print(f'{time() - start:6.3f}ms: successfully reconnected!')
        except Exception as err:
            print(f'{time() - start:6.3f}ms: {type(err).__name__}: {err}')
            retry = 0
    print('{time() - start:6.3f}ms: no further reconnecting.\nclient closed.')
