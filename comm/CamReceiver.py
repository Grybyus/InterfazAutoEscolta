import socket
import struct
import sys
import _thread
import time

def singleton(class_):
  instances = {}
  def getinstance(*args, **kwargs):
    if class_ not in instances:
        instances[class_] = class_(*args, **kwargs)
    return instances[class_]
  return getinstance

@singleton
class CamReceiver(object):
	"""Clase CamReceiver """
	def __init__(self):
		self.sock = None
		self.multicast_group = '239.255.60.60'
		self.server_address = ('', 4876)
		self.eventHandlers = {}
		self.running = False
		self.Escuchando = False
	def thread_lisent(self,tname,delay=0):
		self.Escuchando = True
		self.running=True
		while self.Escuchando:
			if(delay>0):
				time.sleep(delay)
			data, address = self.sock.recvfrom(1024)
			ID = struct.unpack("H",(data[-11:-13:-1]))[0]#0
			F2 = struct.unpack("f",(data[-1:-5:-1])[::-1])[0]#1
			F1 = struct.unpack("f",(data[-5:-9:-1])[::-1])[0]#2

			D4 = struct.unpack("h",(data[-1:-3:-1])[::-1])[0]#3
			D3 = struct.unpack("h",(data[-3:-5:-1])[::-1])[0]#4
			D2 = struct.unpack("h",(data[-5:-7:-1])[::-1])[0]#5
			D1 = struct.unpack("h",(data[-7:-9:-1])[::-1])[0]#6

			E2 = struct.unpack("i",(data[-1:-5:-1])[::-1])[0]#7
			E1 = struct.unpack("i",(data[-5:-9:-1])[::-1])[0]#8

			C8 = struct.unpack("b",(data[-1:-2:-1])[::-1])[0]#9
			C7 = struct.unpack("b",(data[-2:-3:-1])[::-1])[0]#10
			C6 = struct.unpack("b",(data[-3:-4:-1])[::-1])[0]#11
			C5 = struct.unpack("b",(data[-4:-5:-1])[::-1])[0]#12
			C4 = struct.unpack("b",(data[-5:-6:-1])[::-1])[0]#13
			C3 = struct.unpack("b",(data[-6:-7:-1])[::-1])[0]#14
			C2 = struct.unpack("b",(data[-7:-8:-1])[::-1])[0]#15
			C1 = struct.unpack("b",(data[-8:-9:-1])[::-1])[0]#16

			uD4 = struct.unpack("H",(data[-1:-3:-1])[::-1])[0]#17
			uD3 = struct.unpack("H",(data[-3:-5:-1])[::-1])[0]#18
			uD2 = struct.unpack("H",(data[-5:-7:-1])[::-1])[0]#19
			uD1 = struct.unpack("H",(data[-7:-9:-1])[::-1])[0]#20

			uE2 = struct.unpack("I",(data[-1:-5:-1])[::-1])[0]#21
			uE1 = struct.unpack("I",(data[-5:-9:-1])[::-1])[0]#22

			uC8 = struct.unpack("B",(data[-1:-2:-1])[::-1])[0]#23
			uC7 = struct.unpack("B",(data[-2:-3:-1])[::-1])[0]#24
			uC6 = struct.unpack("B",(data[-3:-4:-1])[::-1])[0]#25
			uC5 = struct.unpack("B",(data[-4:-5:-1])[::-1])[0]#26
			uC4 = struct.unpack("B",(data[-5:-6:-1])[::-1])[0]#27
			uC3 = struct.unpack("B",(data[-6:-7:-1])[::-1])[0]#28
			uC2 = struct.unpack("B",(data[-7:-8:-1])[::-1])[0]#29
			uC1 = struct.unpack("B",(data[-8:-9:-1])[::-1])[0]#30
			print((ID,F1,F2,) )
			if(str(ID) in self.eventHandlers):
				for h,o in self.eventHandlers[str(ID)]:
					try:
						h(o,(ID,F1,F2,D1,D2,D3,D4,E1,E2,C1,C2,C3,C4,C5,C6,C7,C8,uD1,uD2,uD3,uD4,uE1,uE2,uC1,uC2,uC3,uC4,uC5,uC6,uC7,uC8,) )
					except Exception as ez:
						print(ez)
						print("La función no es un callback")
		self.running=False

	def open(self):
		if(not self.running):
			# Create the socket
			#self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			#Bind to the server address
			#self.sock.bind(self.server_address)
			# Tell the operating system to add the socket to the multicast group
			# on all interfaces.
			#group = socket.inet_aton(self.multicast_group)
			#mreq = struct.pack('4sL', group, socket.INADDR_ANY)
			#self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
			# http://stackoverflow.com/questions/603852/multicast-in-python
			MCAST_GRP = '239.255.60.60'
			MCAST_PORT = 4876

			self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

			self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

			self.sock.bind(('', MCAST_PORT))
			mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)

			self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
			try:
				self.thread = _thread.start_new_thread( self.thread_lisent, ("Thread-1", 0, ) )
			except Exception as e:
				print(e)
				print ("Error: unable to start thread")
		else:
			print ("thread ya funcionando")

	def close(self):
		self.Escuchando=False

	def addEventHandler(self,hexID,obj,handler):
		if(str(hexID) in self.eventHandlers):
			self.eventHandlers[str(hexID)].append((handler,obj,))

		else:
			self.eventHandlers[str(hexID)]=[(handler,obj,)]
			#print(self.eventHandlers)

	def removeEventHandler(self,hexID,obj,handler):
		try:
			self.eventHandlers[str(hexID)].remove((handler,obj,))
		except:
			print("Evento no estaba registrado")
