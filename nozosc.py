#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
# -*- mode: Python -*-

# Le joystick bougé envoie automatiquement des messages knobs 30 et 31
# Protocole sur le port série :

# Au debut ca envoie rien.

# FF arrête tous les envois en cours
# A0 a AC  Les trucs qui oscillent 
# 0 à 31 les knobs : 2 messages FF numeroknob 00 FF
# N'importe quelle autre valeur va arrêter un 
# F0 Donne le type de nozoid  "MMO3" : FF F0 4D 33
# F1 ralenti
# F2 accélère
# 

import sys
from serial.tools import list_ports
import serial,time
from threading import Thread
import gstt,socket
import struct
from OSC import OSCServer, OSCClient, OSCMessage
import types
from sys import platform

#oscIPin = "192.168.42.194"
#oscIPin = "127.0.0.1"
oscIPin = socket.gethostbyname(socket.gethostname())
oscPORTin = 8001
oscpathin = ""

#oscIPout = ""
oscIPout = "10.255.255.194"
#oscIPout = socket.gethostbyname(socket.gethostname())
oscPORTout = 8001
#oscPORTout = 8002

oscdevice = 0

NozMsg=[0,0,0,0]

print("")
print("OSCServer")
print ("M controller is receiving on ", oscIPin, ":",str(oscPORTin))
#oscserver = OSCServer( ("192.168.42.194", 8001) )
oscserver = OSCServer( (oscIPin, oscPORTin) )
oscserver.timeout = 0
OSCRunning = True
print oscserver.address()


def handle_timeout(self):
    self.timed_out = True



def twoDigitHex( number ):
   return '%02x' % number
   
def send(channel):
    Mser.write([channel]) 
    
def XXXNozMsg(channel,value):
    
    print channel
    print value
    
    
#
# OSC messages handlers
#
   
oscserver.handle_timeout = types.MethodType(handle_timeout, oscserver)


osclient = OSCClient()
osclientme = OSCClient()
oscmsg = OSCMessage()

#oscaddress="/on"

# sendosc(oscaddress, [arg1, arg2,...])

def sendosc(oscaddress,oscargs):
#def sendosc(oscargs):
    
    # also works : osclient.send(OSCMessage("/led", oscargs))

    oscpath = oscaddress.split("/")
    pathlength = len(oscpath)

    oscmsg = OSCMessage()

    if oscpath[2] == "name":
	print "we are asked to send a name"
	oscmsg.setAddress(oscaddress)
	oscmsg.append(oscargs)

    if oscpath[2] == "status":
	print "we are asked to send a status"
	oscmsg.setAddress(oscaddress)
	oscmsg.append(oscargs)

    if oscpath[2] == "knob":
	print "we are asked to send a knob value"
	oscmsg.setAddress(''.join((oscaddress,"/",oscargs[0])))
	oscmsg.append(int(oscargs[1:100]))
	
    if oscpath[2] == "osc":
	#print "we are asked to send continusouly an osc value"
	oscmsg.setAddress(''.join((oscaddress,"/",oscargs[0])))
	oscmsg.append(int(oscargs[1:100]))
	
    #print "here we are sendosc function"
    #print "path:",oscaddress,"pathlength:", pathlength,"oscpath:", oscpath,"args:", oscargs


    #oscmsg.setAddress(''.join((oscaddress,"/",oscargs)))

    #oscmsg.append(oscargs[0])

    #oscmsg.append(oscargs)
    
    print "sending : ",oscmsg
    try:
        osclient.sendto(oscmsg, (oscIPout, oscPORTout))
        oscmsg.clearData()
    except:
        print ('Connection refused at ',oscIPout)
        pass
    #time.sleep(0.001)



# sendme(oscaddress, [arg1, arg2,...])
osclientme.connect((oscIPin, oscPORTin)) 

def sendme(oscaddress,oscargs):
#def sendme(oscargs):
        
    oscmsg = OSCMessage()
    oscmsg.setAddress(oscaddress)
    oscmsg.append(oscargs)
    
    print "sending me: ",oscmsg, oscargs
    try:
        osclientme.sendto(oscmsg, (oscIPin, oscPORTin))
        oscmsg.clearData()
    except:
        print ('Connection to mycontroller refused')
        pass
    #time.sleep(0.001)
  
  
  
# RAW OSC Frame available ? 
def osc_frame():

    # clear timed_out flag
    #print "frame"
    oscserver.timed_out = False
    # handle all pending requests then return
    
    while not oscserver.timed_out:
        oscserver.handle_request()


    
#
# OSC messages handlers
#
   
# default handler 
def nozhandler(path, tags, args, source):

	
	oscpath = path.split("/")
	pathlength = len(oscpath)
	print ""
	print "default handler"
	print "path:",path,"pathlength:", pathlength,"oscpath:", oscpath,"args:", args

	# /cc/number value
	if oscpath[1] == "cc" :
		number = int(oscpath[2])
		value = int(args[0])
		gstt.cc[number] = value    



# /on
def nozon(path, tags, args, source):
    global oscIPout,oscdevice,controlmatrix

    user = ''.join(path.split("/"))
    #print "New OSC Client : " + str(source[0])
    oscIPout = str(source[0])
    osclient.connect((oscIPout, oscPORTout))
    print ("Sending on ", oscIPout, ":",str(oscPORTout))
    status("NozOSC ON")
    print ("Stop Com from Nozoid")
    Mser.write([0xFF])
    print ("asking for with nozoid type...")
    Mser.write([0xF0])

# /stop
def nozstop(path, tags, args, source):

    print ("Stop Com from Nozoid")
    Mser.write([0xFF]) 
#    time.sleep(1)
    print "In_Waiting garbage msg # after 0xFF sent:",Mser.in_waiting
#    time.sleep(1)

    while Mser.in_waiting != 0:
        print "Still",Mser.in_waiting,"In_Waiting garbage msg after 0xFF sent"
	Mser.read()
    
# /name 
def nozname(path, tags, args, source):

    print ("asking for my nozoid name...")
    Mser.write([0xF0])

#    time.sleep(1)
#    print "In_Waiting garbage msg # after 0xF0 sent:",Mser.in_waiting
#    time.sleep(1)
#    for i in range(2):
#        print "!!"
#        print twoDigitHex(ord(Mser.read()[0])), twoDigitHex(ord(Mser.read()[0])), twoDigitHex(ord(Mser.read()[0])), twoDigitHex(ord(Mser.read()[0]))
#    print "In_Waiting garbage msg # after cleaning up try:",Mser.in_waiting
#    time.sleep(1)

#    print ''.join((NozMsg[2],NozMsg[3]))
    
# /lfo
def nozlfo(path, tags, args, source):
	print "LFO"
	print "P:",path,",T:",tags,",A:",args,",S:",source
	print ("LFO ", args[0], "asked")
	Mser.write([0xA2 + int(args[0])]) # 0xA3 : LFO 1 / 0xA4 : LFO 2  / 0xA5 : LFO 3 


# /osc
def nozosc(path, tags, args, source):
	#print "OSC"
	#print ("OSC ", args[0], "asked")
	Mser.write([0x9F + int(args[0])]) # 0xA0 : OSC 1 / 0xA1 : OSC 2  / 0xA2 : OSC 3 

# /down
def nozdown(path, tags, args, source):
	#print ("UP ", args[0], "asked")
	#print "Path:",path,",Tags:",tags,",Args:",args,",Source:",source
	if args:
		Mser.write([0xF1,int(args[0])]) # 0xF1 slowing down flow with argument
	else:
		Mser.write([0xF1]) # 0xF1 slowing down flow

# /up
def nozup(path, tags, args, source):
	#print ("UP ", args[0], "asked")
	#print "Path:",path,",Tags:",tags,",Args:",args,",Source:",source
	if args:
		Mser.write([0xF2,int(args[0])]) # 0xF2 speeding up with argument
	else:
		Mser.write([0xF2]) # 0xF2 speeding up flow

# /knob
def nozknob(path, tags, args, source):
	print ("KNOB", args[0], "asked")
	Mser.write([0 + int(args[0])]) # 0xA0 : OSC 1 / 0xA1 : OSC 2  / 0xA2 : OSC 3 


# Send text to status display widget
def nozstatus(path, tags, args, source):
    sendosc("/nozoid/status", args[0])

# registering all OSC message handlers

oscserver.addMsgHandler( "/nozoid/on", nozon )
oscserver.addMsgHandler( "/nozoid/stop", nozstop )
oscserver.addMsgHandler( "default", nozhandler )
oscserver.addMsgHandler( "/nozoid/name", nozname )
oscserver.addMsgHandler( "/nozoid/lfo", nozlfo )
oscserver.addMsgHandler( "/nozoid/osc", nozosc )
oscserver.addMsgHandler( "/nozoid/up", nozup )
oscserver.addMsgHandler( "/nozoid/down", nozdown )
oscserver.addMsgHandler( "/nozoid/knob", nozknob )
oscserver.addMsgHandler( "/nozoid/status", nozstatus )


#
# Running...
#
    
        
# Search for nozoid

print("")
print("Available serial devices")
ports = list(list_ports.comports())
for p in ports:
    print(p)

try:

    # Find serial port
    if  platform == 'darwin':
        sernozoid = next(list_ports.grep("Arduino Due"))
    if  platform == 'linux2':
        sernozoid = next(list_ports.grep("ACM"))

    print "Serial Picked for Nozoid :",sernozoid[0]
    Mser = serial.Serial(sernozoid[0],115200)
    #Mser = serial.Serial(gstt.sernozoid[0],115200,timeout=5)
    print "Serial connection..."
    print "Device..." 
    print(Mser.is_open)

	# Serial port sync
    print "In_Waiting garbage msg # at the serial opening:",Mser.in_waiting
    
    while Mser.in_waiting != 0:
        print "Still",Mser.in_waiting,"In_Waiting msg to flush at the opening"
        Mser.read()

    #sendme("/stop",1)
    #sendme("/on",1)

    # infinite loop display Nozoid message
    # Todo transfer to a separate thread.
    Mser.write([0xFF])

    #print ("asking for with nozoid type...")
    #the serial way please
    #Mser.write([0xF0])
    #or the OSC way please !
    sendme("/nozoid/name","")
    
    while True:

        #print "loop"
        osc_frame()

	if Mser.in_waiting != 0:        
         NozMsg = Mser.read(4)

         if ord(NozMsg[1]) < 160:
            (val,) = struct.unpack_from('>H', NozMsg, 2)
            #print '/nozoid//knob'.join((str(ord(NozMsg[1]))," ",NozMsg[0:2].encode('hex'),":",str(val)))
            #sendosc("/nozoid/knob",''.join((str(ord(NozMsg[1])),NozMsg[0:2].encode('hex'),":",str(val))))
            sendosc("/nozoid/knob",''.join((str(ord(NozMsg[1])),str(val))))
        
         if ord(NozMsg[1]) >= 0xA0 and ord(NozMsg[1]) < 0xF0:
            (val,) = struct.unpack_from('>h', NozMsg, 2)
            #print type(NozMsg[0:2].encode('hex'))
            #print type(ord(val))
            #print '/nozoid/oscitruc'.join((str(ord(NozMsg[1])-0x9F)," ",NozMsg[0:2].encode('hex'),":",str(val)))
            sendosc("/nozoid/osc",''.join((str(ord(NozMsg[1])-0x9F),str(val))))

         if ord(NozMsg[1]) == 0xF0:   
		print ''.join((NozMsg[2],NozMsg[3]))
		sendosc("/nozoid/name",''.join((NozMsg[2],NozMsg[3])))


except StopIteration:
    print ("No Nozoid device found")
    Mser = False
    
if Mser != False:
    pass
 






