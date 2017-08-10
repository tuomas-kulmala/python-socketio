import time
import random
import eventlet

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from threading import Thread, Event

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

thread = Thread()
thread_stop_event = Event()

eventlet.monkey_patch()

class RandomFigures(Thread):
    def __init__(self):
        self.delay = 1
        self.min = 0
        self.max = 10
        super(RandomFigures, self).__init__()

    def figure_generator(self):
        while not thread_stop_event.isSet():
            figure = random.randint(self.min, self.max)
            print (figure)
            socketio.emit('random_figure', figure, broadcast=True)
            time.sleep(self.delay)

    def run(self):
        self.figure_generator()


@socketio.on('my message')
def handle_message(message):
    print('received message: ' + message['data'])
    emit('my_response', message['data'] + 'sent back', broadcast=True)


@socketio.on('start_random')
def start_random():
    print ('start random called')
    global thread

    if not thread.isAlive():
        thread_stop_event.clear()
        print ('Starting thread')
        thread = RandomFigures()
        thread.start()
    else:
        print ('Thread already started')


@socketio.on('end_random')
def start_random():
    print ('end random called')
    thread_stop_event.set()


@app.route("/")
def hello():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app)