import os
from kivy.app import App
from kivy.event import EventDispatcher
from kivy.properties import OptionProperty
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.lang.builder import Builder
from kivy.logger import Logger
from kivy.clock import Clock
from comqueue.client import Client


Builder.load_string("""
<MainScreen>:
    Screen:
        name: 'not connected'
        Label:
            text: 'connecting to server...'
            font_size: 20
    Screen:
        name: 'connected'
        Label:
            text: 'connected'
            font_size: 50
""")


class MainScreen(ScreenManager):
    pass


class TestClientApp(App):
    def __init__(self, **kwargs):
        super(TestClientApp, self).__init__(**kwargs)
        self.controller = TestClient()
        if self.controller.state == 'connected':
            Clock.schedule_interval(self.greet, 1)

    def build(self):
        return MainScreen(transition=FadeTransition())

    def greet(self, *args):
        self.controller.send('greet', ['hallo'])

    def switch_screen(self, screen_name):
        self.root.current = screen_name


class TestClient(Client):
    def __init__(self):
        self.state = 'not connected'
        super(TestClient, self).__init__(os.path.join(os.getcwd(), 'comqueue', 'config.json'))

    def connect(self, *args):
        try:
            super(TestClient, self).connect()
        except Exception as err:
            Logger.error(f'{self.__class__.__name__}: {type(err).__name__}: {err}')
            self.not_connected()
        else:
            Logger.info(f'{self.__class__.__name__}: connection established!')
            self.connected()

    def send(self, command, data):
        try:
            super(TestClient, self).send(command, data)
        except Exception as err:
            Logger.error(f'{self.__class__.__name__}: {type(err).__name__}: {err}')
            self.not_connected()
        else:
            Logger.info(f'{self.__class__.__name__}: greet command sent.')

    def connected(self):
        self.state = 'connected'
        Clock.schedule_once(self.switch, 0)

    def not_connected(self):
        self.state = 'not connected'
        Clock.schedule_once(self.switch, 0)
        Clock.schedule_once(self.connect, 3)

    def switch(self, *args):
        App.get_running_app().switch_screen(self.state)




if __name__ == '__main__':
    TestClientApp().run()