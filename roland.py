from time import time, sleep as wait
import RPi.GPIO as GPIO
from utils import clamp
import wiringpi

## Pins

# Motor
IN1 = 20 # left forward
IN2 = 21 # left back
IN3 = 19 # right forward
IN4 = 26 # right back
ENA = 16 # left speed (pwm)
ENB = 13 # right speed (pwm)

# RGB module pin
LED_R = 22
LED_G = 27
LED_B = 24

# Infrared sensor pins (BCM ports)
TRACK_SENSOR_LEFT_PIN_1  = 3
TRACK_SENSOR_LEFT_PIN_2  = 5
TRACK_SENSOR_RIGHT_PIN_1 = 4
TRACK_SENSOR_RIGHT_PIN_2 = 18

# Servo pin
SERVO_PIN = 4

# Buzzer pin
BUZZER_PIN = 10

# Ultrasonic pins
ECHO_PIN = 0
TRIG_PIN = 1

# Inits the motors.
def init():
	
	# Set the GPIO port to BCM encoding mode.
	GPIO.setmode(GPIO.BCM)
	
	# LEDs
	GPIO.setup(LED_R, GPIO.OUT)
	GPIO.setup(LED_G, GPIO.OUT)
	GPIO.setup(LED_B, GPIO.OUT)

	GPIO.setwarnings(False)

	# Motors
	GPIO.setup(ENA, GPIO.OUT, initial = GPIO.HIGH)
	GPIO.setup(IN1, GPIO.OUT, initial = GPIO.LOW)
	GPIO.setup(IN2, GPIO.OUT, initial = GPIO.LOW)
	GPIO.setup(ENB, GPIO.OUT, initial = GPIO.HIGH)
	GPIO.setup(IN3, GPIO.OUT, initial = GPIO.LOW)
	GPIO.setup(IN4, GPIO.OUT, initial = GPIO.LOW)

	global pwm_ENA, pwm_ENB
	# pulse width modulation: pin 16 - 2000Hz
	pwm_ENA = GPIO.PWM(ENA, 2000)
	pwm_ENB = GPIO.PWM(ENB, 2000)

	# Track sensor
	GPIO.setup(TRACK_SENSOR_LEFT_PIN_1,  GPIO.IN)
	GPIO.setup(TRACK_SENSOR_LEFT_PIN_2,  GPIO.IN)
	GPIO.setup(TRACK_SENSOR_RIGHT_PIN_1, GPIO.IN)
	GPIO.setup(TRACK_SENSOR_RIGHT_PIN_2, GPIO.IN)

	# Ultra sensor
	GPIO.setup(ECHO_PIN, GPIO.IN)
	GPIO.setup(TRIG_PIN, GPIO.OUT)
	'''
	# buzzer setup
	global pwm_BZZ
	GPIO.setup(BUZZER_PIN, GPIO.OUT)
	pwm_BZZ = GPIO.PWM(BUZZER_PIN, 50) // TODO provide correct frequency
	pwm_BZZ.start(100)

	# servo setup
	global pwm_SRV
	GPIO.setup(SERVO_PIN, GPIO.OUT)
	pwm_SRV = GPIO.PWM(SERVO_PIN, 40) // TODO provide correct frequency

	pwm_SRV.start(100)
	'''
	# ------- wiringpi -------

	# buzzer setup
	wiringpi.wiringPiSetup()
	wiringpi.pinMode(BUZZER_PIN, 1)
	wiringpi.softPwmCreate(BUZZER_PIN, 0, 100)

	# servo setup
	wiringpi.pinMode(SERVO_PIN, GPIO.OUT)
	wiringpi.softPwmCreate(SERVO_PIN, 0, 100)

	wiringpi.softPwmWrite(BUZZER_PIN, 100)
	
	print('Robot loaded.')

def motor(left: int, right: int):
	pwm_ENA.start(abs(left))
	pwm_ENB.start(abs(right))
	GPIO.output(IN1, GPIO.HIGH if left  > 0  else GPIO.LOW)
	GPIO.output(IN2, GPIO.LOW  if left  >= 0 else GPIO.HIGH)
	GPIO.output(IN3, GPIO.HIGH if right > 0  else GPIO.LOW)
	GPIO.output(IN4, GPIO.LOW  if right >= 0 else GPIO.HIGH)

def led(r: bool, g: bool, b: bool):
	GPIO.output(LED_R, GPIO.HIGH if r else GPIO.LOW)
	GPIO.output(LED_G, GPIO.HIGH if g else GPIO.LOW)
	GPIO.output(LED_B, GPIO.HIGH if b else GPIO.LOW)

# Move the servo into an absolute position
def servo_absolute(degree: float):
	degree = (int) (15 - (clamp(degree, -90, 90) / 9))
	wiringpi.softPwmWrite(SERVO_PIN, degree)
	'''
	pwm_SRV.changeDutyCycle(degree)
	'''

# Return the track sensors' readings
def track_sensor():
	ts1 = GPIO.input(TRACK_SENSOR_LEFT_PIN_1)
	ts2 = GPIO.input(TRACK_SENSOR_LEFT_PIN_2)
	ts3 = GPIO.input(TRACK_SENSOR_RIGHT_PIN_1)
	ts4 = GPIO.input(TRACK_SENSOR_RIGHT_PIN_2)
	return (ts1, ts2, ts3, ts4)

# Haha robot go brr
def buzzer(pw: float):
	wiringpi.softPwmWrite(BUZZER_PIN, pw)
	'''
	pwm_BZZ.changeDutyCycle(pw)
	'''

# Return the ultrasound sensor's reading in centimeters
def ultra_sensor():

	GPIO.output(TRIG_PIN, GPIO.HIGH)
	wait(0.000015)
	GPIO.output(TRIG_PIN, GPIO.LOW)

	while not GPIO.input(ECHO_PIN):
		pass

	t1 = time()
	while GPIO.input(ECHO_PIN):
		pass
	t2 = time()

	return ((t2 - t1) * 340 / 2) * 100

# Clean up everything
def clean_up():
	pwm_ENA.stop()
	pwm_ENB.stop()

	'''
	pwm_SRV.stop()
	pwm_BZZ.stop()
	'''

	GPIO.cleanup()
