from omxplayer import OMXPlayer
import time
import RPi.GPIO as GPIO

# Constants
pulsePin = 26 # White to Red
hookPin = 19 # Green to Brown
hookDebounce = 0.1
debounceTime = 100
pollInterval = 0.5
phoneNumLength = 4 
lastDigitPosition = -1
path = './recordings/'

# Variables
state = 0
number = 0
phoneNumber = []
isInterrupt = False
startTime = time.time()
player = OMXPlayer(path + 'dialtone.wav')

GPIO.setmode(GPIO.BCM)
GPIO.setup(pulsePin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(hookPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def countPulse(channel):
	global startTime
	global number
	number = number + 1
	startTime = time.time()

def selectRecording(number):
	if number == 1:
		print "Play Track 1"
		return 'Aela.wav'
	elif number == 2:
		print "Play Track 2"
		return 'Rudy.wav'
	elif number == 3:
		print "Play Track 3"
		return 'imperial-march.mp3'
	elif number == 4:
		print "Play Track 4"
		return 'Maureen.wav'
	elif number == 5:
		print "Play Track 5"
		return 'Monty.wav'
	elif number == 6:
		print "Play Track 6"
		return 'Mariette.wav'
	else:
		print "No Track"
		return 'operator.wav'

# Continously run loop
while True:
	# Check for reset condition: receiver on hook
	if GPIO.input(hookPin) == False:
		time.sleep(hookDebounce)
		if GPIO.input(hookPin) == False:
			state = 0
	
	# init state: reset variables and remove interrupt
	if state == 0:
		number = 0
		phoneNumber = []
                
		if isInterrupt == True:
                        print "RESET"
                        """
                        Stop the player, causing it to quit
                        """
                        player._player_interface.Stop()
                        player.stopEvent(player)
                
                        # needed to completely stop the previous track for somereason 
                        player = OMXPlayer(path + 'Blank.wav')
                        player.play()
                
                        """
                        Stop the player, causing it to quit
                        """
                        player._player_interface.Stop()
                        player.stopEvent(player)
                
			GPIO.remove_event_detect(pulsePin)
			isInterrupt = False
			
			
			
			
		# check if the receiver is taken off the hook
		if GPIO.input(hookPin) == True:
			time.sleep(hookDebounce)
			state = 1
	
	# dial tone state: start interrupt, play dial tone
	elif state == 1:
                
		player = OMXPlayer(path + 'dialtone.wav')
		player.play()
                
                if isInterrupt == False:
			GPIO.add_event_detect(pulsePin, GPIO.RISING, callback=countPulse, bouncetime=debounceTime)
			isInterrupt = True

		state = 2
	
	# dial number state: fill phone number array with inputs from rotary dial
	elif state == 2:
		if len(phoneNumber) != phoneNumLength:
			if ( (time.time() - startTime) > pollInterval and number != 0 ):
				print number
				phoneNumber.append(number)
				number = 0
			time.sleep(hookDebounce)
		
		# when buffer is full, get the last digit
		elif len(phoneNumber) == phoneNumLength:
			lastDigit = phoneNumber[lastDigitPosition]
			phoneNumber = []
			state = 3
	
	# select track state: based on the last digit, select a recording to play
	elif state == 3:
		recordingToPlay = selectRecording(lastDigit)
		player = OMXPlayer(path + recordingToPlay)
		player.play()
		state = 4
	
	# play state: recording plays until the reset condition is asserted
	elif state == 4:
		state = 4	

	else:
		state = 0
					
