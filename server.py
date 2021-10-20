from flask_socketio import SocketIO, emit
from flask import Flask
from utils import clamp
import roland

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*', logger=False, engineio_logger=False)

roland.init()

# Request for moving around
# BODY: { "left": [-100..100], "right": [-100..100] }
@socketio.on('move', namespace='/io')
def move(data: dict):

	# check if keys in request
	if (not 'left' in data or not 'right' in data or not (type(data['left']) is int or float) or not (type(data['right']) is int or float)) :
		socketio.emit('error', { 'type': 'Incorrect request data', 'description': ' Please use format { "left": [-100..100], "right": [-100..100] }' })
		return

	# convert to integer
	left = int(data['left'])
	right = int(data['right'])

	# clamp value between 0 and 100
	left = clamp(left, -100, 100)
	right = clamp(right, -100, 100)

	# move
	roland.motor(left, right)

# Request for LED
# BODY: { 'r': true | false, 'g': true | false, 'b': true | false }
@socketio.on('led', namespace='/io')
def led(data: dict):

	if (not 'r' in data or not 'g' in data or not 'b' in data or type(data['r']) is not bool or type(data['g']) is not bool or type(data['b']) is not bool):
		socketio.emit('error', { 'type': 'Incorrect request data', 'description': ' Please use { "r": true | false, "g": true | false, "b": true | false }' })
		return

	roland.led(data['r'], data['g'], data['b'])

# STOP request, no body required
@socketio.on('stop', namespace='/io')
def stop():
	roland.clean_up()

# Get tracksensor info
# RETURNS: { "data": [[0..1], [0..1], [0..1], [0..1]] }
@socketio.on('tracksensor', namespace='/io')
def sensor():
	emit('return-tracksensor', { 'data':  roland.track_sensor() })

# Get tracksensor info
@socketio.on('ultrasensor', namespace='/io')
def sensor():
	emit('return-ultrasensor', { 'data':  roland.ultra_sensor() })

# Set servo angle
# BODY: { "degree": [-90..90] }
@socketio.on('servo', namespace='/io')
def servo(data: dict):

	if not 'degree' in data or type(data['degree']) is not int:
		socketio.emit('error', { 'type': 'Incorrect request data', 'description': ' Please use { "degree": [-90..90] }' })
		return

	roland.servo_absolute(data['degree'])

# Buzz
# BODY: { "pw": [0..100] }
@socketio.on('buzzer', namespace='/io')
def buzzer(data: dict):

	if not 'pw' in data or type(data['pw']) is not int:
		socketio.emit('error', { 'type': 'Incorrect request data', 'description': ' Please use { "pw": [0..100] }' })
		return

	roland.buzzer(data['pw'])
