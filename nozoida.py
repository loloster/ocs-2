#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
# -*- mode: Python -*-

# Le joystick bougé envoie automatiquement des messages knobs 30 et 31
# Protocole sur le port série :

# Au debut ca envoie rien.

# FF arrête tous les envois en cours
# A0 a #AC  Les trucs qui oscillent 
# 0 à 31 les knobs : 2 messages FF numeroknob 00 00 00FF
# N'importe quelle autre valeur va arrêter un 
# F0 Donne le type de nozoid  "MMO3" : FF F0 4D 4D 4F 33


import sys
from serial.tools import list_ports
import serial,time
from threading import Thread
import gstt

cc = [0] * 256
MESSAGE = 0xFF
sermsg = [0,0,0,0,0,0]

def twoDigitHex( number ):
   return '%02x' % number
   
def send(Mser, channel):
    Mser.write([channel]) 
    
def NozMsg(channel,value):
    
    print channel
    print value

    
def stop(Mser):

#    print "in stop()"
    Mser.write([0xFF]) 

    print "In_Waiting garbage msg # after 0xFF sent:",Mser.in_waiting
    while Mser.in_waiting != 0:
        print "Still",Mser.in_waiting,"In_Waiting garbage msg after 0xFF sent"
	Mser.read()
	
	    
def getname(Mser):
    
#    print "in getname()"
    stop(Mser)

    Mser.write([0xF0])

    print "In_Waiting garbage msg # after 0xF0 sent:",Mser.in_waiting
#    while Mser.in_waiting != 0:
#        print "Still",Mser.in_waiting,"In_Waiting garbage msg after 0xF0 sent:",Mser.in_waiting
#	Mser.read()

    getmsg(Mser) 
    getmsg(Mser)
    print "In_Waiting garbage msg # after cleaning up try:",Mser.in_waiting
    
    
def getmsg(Mser):
#	print "In getmsg()"

	valhxx = ""

	sermsg[0] = ord(Mser.read())
	if sermsg[0] == MESSAGE:
		channel = ord(Mser.read()[0])
		
#		print "channel:",channel

		# correct Knob packet ?
		if channel < 32:
#			print "received a knob msg:",channel

			sermsg[1]= twoDigitHex(channel)
			sermsg[2]= twoDigitHex(ord(Mser.read()[0]))
			sermsg[3]= twoDigitHex(ord(Mser.read()[0]))

			print sermsg[1], sermsg[2], sermsg[3]
			if sermsg[2]== "00" and sermsg[3]== "00":
#				print "reading end of channel msg",channel

				sermsg[4]= twoDigitHex(ord(Mser.read()[0]))
				sermsg[5]= twoDigitHex(ord(Mser.read()[0]))
				valhxx = "".join((str(sermsg[2]),str(sermsg[3]),str(sermsg[4]),str(sermsg[5])))
				NozMsg(sermsg[1],valhxx)

		# OSC/LFO... packet.
		elif (channel >= 0xA0 and channel <= 0xAC) or channel == 0xF0:
			sermsg[1]= twoDigitHex(channel)
			sermsg[2]= twoDigitHex(ord(Mser.read()[0]))
			sermsg[3]= twoDigitHex(ord(Mser.read()[0]))
			sermsg[4]= twoDigitHex(ord(Mser.read()[0]))
			sermsg[5]= twoDigitHex(ord(Mser.read()[0]))
			valhxx = "".join((str(sermsg[2]),str(sermsg[3]),str(sermsg[4]),str(sermsg[5])))
			NozMsg(sermsg[1],valhxx)

		# ID packet (MMO3 or OSC2).
		#elif channel == 0xF0:
		#	print "received ID packet…"

		else:
			print "Wrong Packet : ", valhxx

	else:
#		if gstt.debug > 0:
			print "Ditched Packet"
			print sermsg[0]
			

def MSerialinProcess():

    
    while True:
        
        getmsg(Mser)
        time.sleep(0.02)
        
        
# Search for nozoid
def check():
 
    print("")
    print("Available nozoid devices")
    ports = list(list_ports.comports())
    for p in ports:
        print(p)

    try:
        gstt.sernozoid = next(list_ports.grep("ACM1"))
        print "Serial Picked for Nozoid :",gstt.sernozoid[0]
        Mser = serial.Serial(gstt.sernozoid[0],115200)
        #Mser = serial.Serial(gstt.sernozoid[0],115200,timeout=10)
        print "Serial connection..."
        print "Device..." 

        print "In_Waiting garbage msg # at the serial opening:",Mser.in_waiting
        while Mser.in_waiting != 0:
            print "Still",Mser.in_waiting,"In_Waiting msg to flush at the opening"
	    Mser.read()

        getname(Mser)

        raw_input("Press Enter to continue...")

        Mser.write([0x01])
        for i in range(2):
            getmsg(Mser)
        
        raw_input("Press Enter to continue...")

        #Mser.write([0xA4])
        #Mser.write([0xA5])
        #Mser.write([0xA6])
        while True:
            getmsg(Mser)
    
    #Mser.write(bytes([int(113)]))
    #thread = Thread(target=MSerialinProcess, args=())
    #thread.setDaemon(True)
    #thread.start()
    
    except StopIteration:
        print ("No Nozoid device found")
        Mser = False
    
    if Mser != False:
        pass
 

check()
