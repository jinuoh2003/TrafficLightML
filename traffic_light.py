
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

print("Setup LED pins as outputs")

def light_timer(trafficLight, extratime):

    GPIO.setup(23, GPIO.OUT)    # 왼쪽 신호등 red
    GPIO.setup(24, GPIO.OUT)    # 왼쪽 신호등 blue
    GPIO.setup(5, GPIO.OUT)     # 오른쪽 신호등 red 
    GPIO.setup(6, GPIO.OUT)     # 오른쪽 신호등 blue
    try:
        GPIO.output(23, trafficLight[0])   
        GPIO.output(24, trafficLight[1]) 
        GPIO.output(5, trafficLight[2]) 
        GPIO.output(6, trafficLight[3])  
        print("timer start")
        time.sleep(5+extratime)	# 60초+a(알파) 시간 지연
        print("timer end")

    except KeyboardInterrupt:
        GPIO.cleanup()     



    