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

import random
import pysimpledmx
import sys
from serial.tools import list_ports
import serial,time
from threading import Thread
import gstt,socket
import struct
from OSC import OSCServer, OSCClient, OSCMessage
import types
from sys import platform
import argparse

tLfoVal0 =  [0] * 256
tLfoVal1 =  [0] * 256
tLfoDelta = [0] * 256

lfoval0=0
lfoval1=0

argsparser = argparse.ArgumentParser(description="A Scanner Interface Darkly")
#argsparser.add_argument("interface",help="interface to scan")
argsparser.add_argument("-i","--iport",help="Port number receiving OSC commands (8003 by default)",type=int)
argsparser.add_argument("-o","--oport",help="Port number sending OSC commands to LJay (bhorosc.py) (8001 by default)",type=int)
argsparser.add_argument("-n","--nozport",help="Serial port number connected to Nozoïd USB ((ACM)0 by default)",type=int)
args = argsparser.parse_args()

if args.iport:
	iport=args.iport
else:
	iport=gstt.iport

if args.oport:
	oport=args.oport
else:
	oport=gstt.oport

if args.nozport:
	nozport=args.nozport
	print nozport
else:
	nozport=gstt.nozport

def scaleTo127(value):#scale down a short [0,65535] to 127
	return ((value/256)/2)

#DMX
def nozdmx(xy,osc,value):
	#print "hey! i'm nozdmx!"
	#print xy
	#print osc
	#print value
	dmxv=scaleTo127(value+32767)
	if xy == "X":
		senddmx(7,dmxv)#pan
		senddmx(8,dmxv)#change tilt to 180° (see http://static.boomtonedj.com/pdf/manual/43/43105_manuelfroggyledrgbw.pdf)
		#senddmx(9,255)#rotation speed
	if xy == "Y":
		senddmx(21,dmxv)#pan
		senddmx(23,dmxv)#tilt
		#senddmx(25,255)#rotation speed

def joydmx(knob,value):
	#print knob
	#print type(knob)
	#print value
	#print type(value)
	#vrand=random.randint(0,255)
	dmxv=scaleTo127(value)
	print dmxv
	if knob == 30:
		senddmx(7,dmxv)#pan
		senddmx(8,dmxv)#change tilt to 180° (see http://static.boomtonedj.com/pdf/manual/43/43105_manuelfroggyledrgbw.pdf)
		#senddmx(9,dmxv)#rotation speed
	if knob == 31:
		senddmx(21,dmxv)#pan
		senddmx(23,dmxv)#tilt
		#senddmx(25,dmxv)#rotation speed


def senddmx0():
    for channel in range (1,512):
	senddmx(channel,0)

def senddmx(channel, value):

    if gstt.serdmx != "":
        #mydmx.setChannel((channel + 1 ), value, autorender=True)
        # calling render() is better more reliable to actually sending data

        # Some strange bug. Need to add one to required dmx channel is done automatically
        mydmx.setChannel((channel + 1 ), value)
        mydmx.render()
        print "Sending DMX Channel : ", str(channel), " value : ", str(value)



#oscIPin = "192.168.42.194"
#oscIPin = "127.0.0.1"
#oscIPin = "192.168.1.246"
oscIPin = socket.gethostbyname(socket.gethostname())
#oscPORTin = 8003
oscPORTin = iport
oscpathin = ""

#oscIPout = ""
#oscIPout = "10.255.255.194"
oscIPout = socket.gethostbyname(socket.gethostname())
#bhorosc.py
#oscPORTout = 8001
oscPORTout = oport
#oscPORTout = 8002

#OSCServer sam nrhck
oscIPout2 = "192.168.1.10"
oscPORTout2 = 8001

oscdevice = 0

NozMsg=[0,0,0,0]
NozMsgL=[0,0,0,0,0,0]

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


def twoDigit( number ):
   return '%02d' % number

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
	oscmsg.setAddress(''.join((oscaddress,"/",str(int(oscargs[0:2])))))
	oscmsg.append(int(oscargs[2:100]))
	if mydmx:
		joydmx(int(oscargs[0:2]),int(oscargs[2:100]))
	#else:
	#	print oscmsg
	
    if oscpath[2] == "osc":
	#print "we are asked to send continusouly an osc value"
	#print oscargs
	oscmsg.setAddress(''.join((oscaddress,"/",str(int(oscargs[0:2])))))
	oscmsg.append(int(oscargs[2:100]))
	#if mydmx:
	#	nozdmx(gstt.OsciLazCoord[int(oscargs[0:2])],
	#		int(oscargs[0:2]),
	#		int(oscargs[2:100]))

    if oscpath[2] == "lfo":
	#print "we are asked to send continusouly a lfo value"
	oscmsg.setAddress(''.join((oscaddress,"/",str(int(oscargs[0:2])))))
	oscmsg.append(int(oscargs[2:100]))

    if oscpath[2] == "vco":
	#print "we are asked to send continusouly a vco value"
	oscmsg.setAddress(''.join((oscaddress,"/",str(int(oscargs[0:2])))))
	oscmsg.append(int(oscargs[2:100]))

    if oscpath[2] == "mix":
	#print "we are asked to send continusouly a mix value"
	oscmsg.setAddress(''.join((oscaddress,"/",str(int(oscargs[0:2])))))
	oscmsg.append(int(oscargs[2:100]))

    if oscpath[2] == "X":
	print "we are asked to send continusouly a X value"
	oscmsg.setAddress(oscaddress)
	oscmsg.append(oscargs)
	#print oscargs
	gstt.OsciLazCoord[oscargs]="X"
	#print gstt.OsciLazCoord[oscargs]
	#if mydmx:
	#	print oscaddress
	#	print oscargs
	#	#print oscargs[2:100]
	#	#nozdmx(1,int(oscargs[0:2]),int(oscargs[2:100]))

    if oscpath[2] == "Y":
	print "we are asked to send continusouly a Y value"
	oscmsg.setAddress(oscaddress)
	oscmsg.append(oscargs)
	gstt.OsciLazCoord[oscargs]="Y"
	#if mydmx:
	#	print oscaddress
	#	print oscargs
	#	#print oscargs[2:100]
	#	#nozdmx(2,int(oscargs[0:2]),int(oscargs[2:100]))


    if oscpath[2] == "color":
	print "we are asked to change lazer color"
	oscmsg.setAddress(oscaddress)
	if len(oscargs) > 0:
		oscmsg.append(oscargs)


    #print "here we are sendosc function"
    #print "path:",oscaddress,"pathlength:", pathlength,"oscpath:", oscpath,"args:", oscargs


    #oscmsg.setAddress(''.join((oscaddress,"/",oscargs)))

    #oscmsg.append(oscargs[0])

    #oscmsg.append(oscargs)
    

    #print "oscmsg length:",len(oscmsg)
    #print "sending:",oscmsg

    #if len(oscmsg) > 0:

#    try:
	#send to sam nrhck
#	osclient.sendto(oscmsg, (oscIPout2, oscPORTout2))
	#print ('Connection accepted @ sam ',oscIPout2)
#    except:
#	print ('Connection refused @ sam ',oscIPout2)
#        pass

    try:
	osclient.sendto(oscmsg, (oscIPout, oscPORTout))
	oscmsg.clearData()
    except:
	print ('Connection refused at ',oscIPout)
        pass

    #else:
#	print "Hum here in nozosc.py something went wrong with your %r msg" %oscpath[2]
    #time.sleep(0.001)

#    try:
	#send to sam nrhck
#	osclient.sendto(oscmsg, (oscIPout2, oscPORTout2))
	#print ('Connection accepted @ sam ',oscIPout2)
#    except:
	#print ('Connection refused @ sam ',oscIPout2)
#        pass



# sendme(oscaddress, [arg1, arg2,...])
osclientme.connect((oscIPin, oscPORTin)) 

def sendme(oscaddress,oscargs):
#def sendme(oscargs):
        
    oscmsg = OSCMessage()
    oscmsg.setAddress(oscaddress)
    oscmsg.append(oscargs)
    
    #print "sending me: ",oscmsg, oscargs
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

    sendosc("/nozoid/X", 0)
    gstt.X=0
    sendosc("/nozoid/Y", 0)
    gstt.Y=0

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
	#print "LFO"
	#print "P:",path,",T:",tags,",A:",args,",S:",source
	print ("LFO ", args[0], "asked")
	Mser.write([0xA2 + int(args[0])]) # 0xA3 : LFO 1 / 0xA4 : LFO 2  / 0xA5 : LFO 3 


# /osc
def nozosc(path, tags, args, source):
	#print "OSC"
	print ("OSC ", args[0], "asked")
	Mser.write([0x9F + int(args[0])]) # 0xA0 : OSC 1 / 0xA1 : OSC 2  / 0xA2 : OSC 3 

# /vco
def nozvco(path, tags, args, source):
	#print "OSC"
	print ("VCO ", args[0], "asked")
	Mser.write([0xF2 + int(args[0])]) # 0xA0 : OSC 1 / 0xA1 : OSC 2  / 0xA2 : OSC 3

# /mix
def nozmix(path, tags, args, source):
	#print "OSC"
	print ("MIX ", args[0], "asked")
	Mser.write([0xF5 + int(args[0])]) # 0xA0 : OSC 1 / 0xA1 : OSC 2  / 0xA2 : OSC 3

# /down
def nozdown(path, tags, args, source):
	print ("UP ", args[0], "asked")
	#print "Path:",path,",Tags:",tags,",Args:",args,",Source:",source
	if args:
		Mser.write([0xF1,int(args[0])]) # 0xF1 slowing down flow with argument
	else:
		Mser.write([0xF1]) # 0xF1 slowing down flow

# /up
def nozup(path, tags, args, source):
	print ("UP ", args[0], "asked")
	#print "Path:",path,",Tags:",tags,",Args:",args,",Source:",source
	if args:
		Mser.write([0xF2,int(args[0])]) # 0xF2 speeding up with argument
	else:
		Mser.write([0xF2]) # 0xF2 speeding up flow

# /knob
def nozknob(path, tags, args, source):
	print ("KNOB", args[0], "asked")
	Mser.write([0 + int(args[0])]) # 0xA0 : OSC 1 / 0xA1 : OSC 2  / 0xA2 : OSC 3 

# /X
def nozX(path, tags, args, source):
	#print args
	if 0 == len(args):
		print "Current active X trace set to %d" % gstt.X
	else:
		print "Setting active X trace to %d" % args[0]
		#print type(args[0])
	#deactivate currently active osc used
		if gstt.X <= 16:
			Mser.write([0x9F + gstt.X])
		else:
			Mser.write([0xE2 + gstt.X])

		if args[0] <= 16:
			Mser.write([0x9F + int(args[0])])
			#print("/nozoid/X/%d") % (0x00 + int(args[0]))
			sendosc("/nozoid/X",(0x00 + int(args[0])))
		else:
			Mser.write([0xE2 + int(args[0])])
			#print("/nozoid/X/%d") % (0x43 + int(args[0]))
			#sendosc("/nozoid/X",(0x43 + int(args[0])))
			#print("/nozoid/X/%d") % (0x00 + int(args[0]))
			sendosc("/nozoid/X",(0x00 + int(args[0])))

		gstt.X=int(args[0])

# /Y
def nozY(path, tags, args, source):
	#print args
	if 0 == len(args):
		print "Current active Y trace set to %d" % gstt.Y
	else:
		print "Setting active Y trace to %d" % args[0]
		#print type(args[0])
	#deactivate currently active osc used
		if gstt.Y <= 16:
			Mser.write([0x9F + gstt.Y])
		else:
			Mser.write([0xE2 + gstt.Y])

		if args[0] <= 16:
			Mser.write([0x9F + int(args[0])])
			#print("/nozoid/Y/%d") % (0x00 + int(args[0]))
			sendosc("/nozoid/Y",(0x00 + int(args[0])))
		else:
			Mser.write([0xE2 + int(args[0])])
			#print("/nozoid/Y/%d") % (0x43 + int(args[0]))
			#sendosc("/nozoid/Y",(0x43 + int(args[0])))
			#print("/nozoid/Y/%d") % (0x00 + int(args[0]))
			sendosc("/nozoid/Y",(0x00 + int(args[0])))

		gstt.Y=int(args[0])

def nozcolor(path, tags, args, source):
	print "Quelqu'un (je ne sais pas qui) m'a demandé de la couleur…"
	print args
	if 0 == len(args):
		sendosc("/nozoid/color",[])
		print "Hum maybe you should see now what bhorosc.py has answered about colorZ"
		#gstt.color[0]=(gstt.colorX[0] or gstt.colorY[0])
		#print "RX:%d RY:%d R:%d"%(gstt.colorX[0],gstt.colorY[0],gstt.color[0])
		#gstt.color[1]=(gstt.colorX[1] or gstt.colorY[1])
		#print "GX:%d GY:%d G:%d"%(gstt.colorX[1],gstt.colorY[1],gstt.color[1])
		#gstt.color[2]=(gstt.colorX[2] or gstt.colorY[2])
		#print "BX:%d BY:%d B:%d"%(gstt.colorX[2],gstt.colorY[2],gstt.color[2])

	else:
		print "Changing color to R:%d G:%d B:%d" % (args[0], args[1], args[2])
		gstt.color[0]=int(args[0])
		gstt.color[1]=int(args[1])
		gstt.color[2]=int(args[2])
		sendosc("/nozoid/color",[gstt.color[0],gstt.color[1],gstt.color[2]])

def flashdmx(path, tags, args, source):

	for channel in range (1,10):
		vrand=random.randint(0,255)
		senddmx(channel,vrand)

	for channel in range (21,30):
		vrand=random.randint(0,255)
		senddmx(channel,vrand)

	for channel in range (41,44):
		vrand=random.randint(0,255)
		senddmx(channel,vrand)

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
oscserver.addMsgHandler( "/nozoid/vco", nozvco )
oscserver.addMsgHandler( "/nozoid/mix", nozmix )
oscserver.addMsgHandler( "/nozoid/up", nozup )
oscserver.addMsgHandler( "/nozoid/down", nozdown )
oscserver.addMsgHandler( "/nozoid/knob", nozknob )
oscserver.addMsgHandler( "/nozoid/status", nozstatus )
oscserver.addMsgHandler( "/nozoid/X", nozX )
oscserver.addMsgHandler( "/nozoid/Y", nozY )
oscserver.addMsgHandler( "/nozoid/color", nozcolor )
oscserver.addMsgHandler( "/nozoid/flashdmx", flashdmx )


#
# Running...
#
    
        
# Search for nozoid

print("")
print("Available serial devices")
ports = list(list_ports.comports())
for p in ports:
    print(p)

#raw_input("Will try to select Last Serial Port\nPress Enter to continue...")

try:

    # Find nozoid serial port
    if  platform == 'darwin':
        sernozoid = next(list_ports.grep("Arduino Due"))
    if  platform == 'linux2':
        print "ACM"+str(nozport)
        sernozoid = next(list_ports.grep("ACM"+str(nozport)))


    print "Serial Picked for Nozoid :",sernozoid[0]
    Mser = serial.Serial(sernozoid[0],115200)
    #Mser = serial.Serial(sernozoid[0],230400)
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
    Mser.write([0xF0])
    #or the OSC way please !
    sendme("/nozoid/name","")

except StopIteration:
    print ("No Nozoid device found")
    Mser = False
    
if Mser != False:
    pass

    try:
    # Find DMX serial port
	if  platform == 'darwin':
		gstt.serdmx = next(list_ports.grep("DMX USB PRO"))
	if  platform == 'linux2':
		gstt.serdmx = next(list_ports.grep("/dev/ttyUSB0"))

	#print "gstt.serdmx", gstt.serdmx
	#raw_input("Press Enter to continue...")

	print ("Serial Picked for DMX : ",gstt.serdmx[0])

	if gstt.serdmx != "":
		mydmx = pysimpledmx.DMXConnection(gstt.serdmx[0])

	senddmx0()
	time.sleep(1)

	vrand=random.randint(0,255)
	senddmx(1,vrand)#dimmer full
	vrand=random.randint(0,255)
	senddmx(3,vrand)#red
	vrand=random.randint(0,255)
	senddmx(4,vrand)#green
	vrand=random.randint(0,255)
	senddmx(5,vrand)#blue
	vrand=random.randint(0,255)
	senddmx(6,vrand)#
	vrand=random.randint(0,255)
	senddmx(7,vrand)#pan
	vrand=random.randint(0,255)
	senddmx(8,vrand)#change tilt to 180° (see http://static.boomtonedj.com/pdf/manual/43/43105_manuelfroggyledrgbw.pdf)
	vrand=random.randint(0,255)
	#senddmx(9,vrand)#rotation speed
	senddmx(9,0)#rotation speed

	vrand=random.randint(0,255)
	senddmx(21,vrand)#pan (see https://www.mhdiffusion.fr/download/notices/xs_15_spot_fra.pdf)
	vrand=random.randint(0,255)
	senddmx(22,0)#pan fine (?)
	vrand=random.randint(0,255)
	senddmx(23,vrand)#tilt
	vrand=random.randint(0,255)
	senddmx(24,0)#tilt fine (?)
	vrand=random.randint(0,255)
	senddmx(25,0)#velocity pan/tilt
	#senddmx(25,255)#velocity pan/tilt
	vrand=random.randint(0,255)
	senddmx(26,255)#dimmer / strob
	vrand=random.randint(0,255)
	senddmx(27,255)#red
	vrand=random.randint(0,255)
	senddmx(28,255)#green
	vrand=random.randint(0,255)
	senddmx(29,255)#blue
	vrand=random.randint(0,255)
#    senddmx(30,vrand)#color macro
	vrand=random.randint(0,255)
#    senddmx(31,vrand)#velocity macro
	vrand=random.randint(0,255)
#    senddmx(32,0)#movement macro
	vrand=random.randint(0,255)
#    senddmx(33,vrand)#globo

	vrand=random.randint(0,255)
	senddmx(41,vrand)
	vrand=random.randint(0,255)
	senddmx(42,vrand)
	vrand=random.randint(0,255)
	senddmx(43,vrand)

	vrand=random.randint(0,255)
#    senddmx(44,255)
	vrand=random.randint(0,255)
#    senddmx(45,255)
	vrand=random.randint(0,255)
#    senddmx(46,vrand)
	vrand=random.randint(0,255)
#    senddmx(47,vrand)
	vrand=random.randint(0,255)

    except StopIteration:
	    print ("No DMX device found")
	    mydmx = False
    if mydmx != False:
	pass
#end DMX exception initialization
#mydmx is *set* to false so can be checked for the following…

    if mydmx:
	#raw_input("DMX On!")
	print "DMX On!"
    else:
	#raw_input("DMX Off!")
	print "DMX Off!"

    while True:

        #print "loop"
	#time.sleep(0.001)
        osc_frame()

	if Mser.in_waiting != 0:        
         NozMsg = Mser.read(4)

         if ord(NozMsg[1]) < 160:
            (val,) = struct.unpack_from('>H', NozMsg, 2)
            #print '/nozoid//knob'.join((str(ord(NozMsg[1]))," ",NozMsg[0:2].encode('hex'),":",str(val)))
            #sendosc("/nozoid/knob",''.join((str(ord(NozMsg[1])),NozMsg[0:2].encode('hex'),":",str(val))))
            sendosc("/nozoid/knob",''.join((twoDigit(ord(NozMsg[1])),str(val))))
        
         if ord(NozMsg[1]) >= 0xA0 and ord(NozMsg[1]) < 0xF0:

	    OrdNozMsg=ord(NozMsg[1])

	    tLfoVal0[OrdNozMsg]=tLfoVal1[OrdNozMsg]

            (val,) = struct.unpack_from('>h', NozMsg, 2)
	    #print NozMsg
            #print type(NozMsg[0:2].encode('hex'))
            #print type(ord(val))
            #print '/nozoid/oscitruc'.join((str(ord(NozMsg[1])-0x9F)," ",NozMsg[0:2].encode('hex'),":",str(val)))

	    tLfoVal1[OrdNozMsg]=val
	    tLfoDelta[OrdNozMsg]=abs(tLfoVal1[OrdNozMsg]-tLfoVal0[OrdNozMsg])
	    #à envoyer comme msg 0xAD(14) et 0xAE(15)
	    #print "delta lfo %x : %d" % (OrdNozMsg, tLfoDelta[OrdNozMsg])

            sendosc("/nozoid/osc",''.join((twoDigit(ord(NozMsg[1])-0x9F),str(val))))

         if ord(NozMsg[1]) == 0xF0:   
	    print ''.join((NozMsg[2],NozMsg[3]))
	    sendosc("/nozoid/name",''.join((NozMsg[2],NozMsg[3])))

         if ord(NozMsg[1]) >= 0xF3 and ord(NozMsg[1]) <= 0xF5:
	    #NozMsgL=NozMsg+Mser.read(2)
            (val,) = struct.unpack_from('>H', NozMsg, 2)
            #(val,) = struct.unpack_from('>L', NozMsgL, 2)
            #print ''.join((str(ord(NozMsg[1])-0x9F)," ",NozMsg[0:2].encode('hex')," ",NozMsg[2:4].encode('hex'),":",str(val)))
            #print ''.join((str(ord(NozMsg[1])-0xF2)," ",NozMsg[0:2].encode('hex')," ",NozMsg[2:4].encode('hex'),":",str(val)))
            #print ''.join((str(ord(NozMsg[1])-0xF2)," ",NozMsg[0:2].encode('hex')," ",NozMsgL[2:6].encode('hex'),":",str(val)))
            #sendosc("/nozoid/osc",''.join((twoDigit(ord(NozMsg[1])-0x9F),str(val))))
            #sendosc("/nozoid/osc",''.join((twoDigit(ord(NozMsg[1])-0x9F),str(val-32767))))
            #sendosc("/nozoid/vco",''.join((twoDigit(ord(NozMsg[1])-0xF2),str(val-32767))))
            sendosc("/nozoid/osc",''.join((twoDigit(ord(NozMsg[1])-0xE2),str(val-32767))))

         if ord(NozMsg[1]) >= 0xF6 and ord(NozMsg[1]) <= 0xF8:
	    #NozMsgL=NozMsg+Mser.read(2)
            (val,) = struct.unpack_from('>h', NozMsg, 2)
            #(val,) = struct.unpack_from('>l', NozMsgL, 2)
            #print ''.join((str(ord(NozMsg[1])-0x9F)," ",NozMsg[0:2].encode('hex')," ",NozMsg[2:4].encode('hex'),":",str(val)))
            #print ''.join((str(ord(NozMsg[1])-0xF5)," ",NozMsg[0:2].encode('hex')," ",NozMsg[2:4].encode('hex'),":",str(val)))
            #print ''.join((str(ord(NozMsg[1])-0xF5)," ",NozMsg[0:2].encode('hex')," ",NozMsgL[2:6].encode('hex'),":",str(val)))
            #sendosc("/nozoid/osc",''.join((twoDigit(ord(NozMsg[1])-0x9F),str(val))))
            #sendosc("/nozoid/mix",''.join((twoDigit(ord(NozMsg[1])-0xF5),str(val))))
            sendosc("/nozoid/osc",''.join((twoDigit(ord(NozMsg[1])-0xE2),str(val))))


'''
except StopIteration:
    print ("No Nozoid or DMX device found")
    print Mser
    Mser = False
    
if Mser != False:
    pass
'''
