import RPi.GPIO as GPIO
import time
import threading
import math

EN=23
RST=24
CLK=22
CCW=27

inMotion=False
totalDist=0 #degree
distanceToGo=0 #degree
speed=0 #RPM
pulseStep=0.9 #degree
minFreq=0.5
n=5 #constant acc speed

def pulse_thread(cnt,freq,port):
	while cnt>0:
		GPIO.output(port,1)
		time.sleep(0.5*1/freq)
		GPIO.output(port,0)
		time.sleep(0.5*1/freq)
		cnt=cnt-1

def speed_thread(curve):
#accDist=distanceToGo/pulseStep*0.33
#2ax=v*v-v0*v0
#v0=0
#v=speed
#x=accDist
#a=v*v/2/x
#freq(n)=freq(n-1)+a*delta_T
	#deltaT=deltaX/V=deltaX/(pulseStep*freq(n-1))
	#assume we accelerate continously after n pulse, so deltaX is n pulseSteps
	#deltaT=n/freq(n-1)
	#freq(n)=freq(n-1)+a*n/freq(n-1)
	global totalDist, speed, CLK, pulseStep, inMotion, minFreq,n
	totalDist=int(totalDist/pulseStep)#convert distance to stepper motor pulses=666
	speed=speed*6/pulseStep		#convert speed to stepper motor pulses/second=freq=33.3
	accDist=int(0.33*totalDist)	#distance travelling at accelerate and decelerate=666
	constDist = totalDist-2*accDist #distance travelling at constant speed
	acc=0.5*speed*speed/accDist	#acceleration, pulses/(seconds*seconds)=0.817
	
	print("accDist=%d\n"%accDist)
	print("acc=%f"%acc)
	print("speed=%d"%speed)
	#acceleration
	minFreq=math.sqrt(2*acc*n) #the first pulse,2*a*1=freq*freq-0
	freq=minFreq
	distToGo=accDist
	while distToGo>0:
		freq=freq+acc*n/freq#=
		if freq>speed:
			freq=speed
#			print("acceleration over flow")
		print("freq=%f"%freq)
		distToGo=distToGo-n
		thread=threading.Thread(target=pulse_thread,args=(n,freq,CLK))
		thread.start()
		thread.join()	
	print("const speed now...")

	#constant speed travel
	thread=threading.Thread(target=pulse_thread,args=(constDist,speed,CLK))
	thread.start()
	thread.join()

	print("deceleration now")
	#deceleration
	distToGo=accDist
	while distToGo>0:
		freq=freq-acc*n/freq
		if freq<0:
			freq=minFreq
			print("freq=%f"%freq)
		distToGo=distToGo-n
		thread=threading.Thread(target=pulse_thread,args=(n,freq,CLK))
		thread.start()	
		thread.join()	

def init_driver():
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(EN,GPIO.OUT)
	GPIO.setup(RST,GPIO.OUT)
	GPIO.setup(CCW,GPIO.OUT)
	GPIO.setup(CLK,GPIO.OUT)
	GPIO.output(EN,1)
	GPIO.output(CLK,0)
	GPIO.output(RST,1)
	print("driver inited..")

def forward():
	GPIO.output(CCW,1)

def reverse():
	GPIO.output(CCW,0)


init_driver()
#thread=threading.Thread(target=speed_thread,args=("trapzoid",))
#thread.start()

while True:
	if inMotion:
		pass
	else:
		print "speed(RPM)..."
		str=input("$:")
		speed=int(str)
		print ("speed=%d"%speed)
		print "distance (degree)..."
		str=input("$:")
		distanceToGo=int(str)
		totalDist=distanceToGo
		print("distance=%d"%distanceToGo)
		if distanceToGo<0:
			reverse()
		else:
			forward()
		inMotion=True

		thread=threading.Thread(target=speed_thread,args=("trapzoid",))
		thread.start()
		print("motion begins")
		thread.join()
		print("motion finishs")
		inMotion=False
