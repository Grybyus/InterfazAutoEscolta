import socket
import struct

class UDPTools(object):
	GENERAL_STRUCT=0
	GPS_STRUCT=1
	MPPT_STRUCT=2
	EXTRAMPPT_STRUCT=3
	BOTONES_STRUCT=4
	s_general = struct.Struct('i 32s')#0
	s_gps = struct.Struct('i f f f i d f')#1 TODO: revisar porque mide 36 si no tiene mucho sentido
	s_dataMPPT = struct.Struct('i f f f i i i i f')#2
	s_dataExtraMPPT = struct.Struct('i f f f 20s')#3
	s_dataBotones = struct.Struct('i i i i i 16s')#4

	@staticmethod
	def Send_GPS(lat,lon,alt,err,lastUpdate,heading):
		msg = (UDPTools.GPS_STRUCT,lat,lon,alt,err,lastUpdate,heading)
		#UDP
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
		sock.sendto(UDPTools.s_gps.pack(*msg), ("239.192.0.100", 4242))
	@staticmethod
	def Send_MPPT(Vin,Iin,Vout,bulr,out,noe,undv,t):
		msg = (UDPTools.MPPT_STRUCT,Vin,Iin,Vout,bulr,out,noe,undv,t)
		#UDP
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
		sock.sendto(UDPTools.s_dataMPPT.pack(*msg), ("239.192.0.100", 4242))
	@staticmethod
	def Send_EXTRA(t1,t2,corriente):
		msg = (UDPTools.EXTRAMPPT_STRUCT,t1,t2,corriente," ")
		#UDP
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
		sock.sendto(UDPTools.s_dataExtraMPPT.pack(*msg), ("239.192.0.100", 4242))
	@staticmethod
	def Send_BOTONES(mppt,luces,fan,bateria):
		msg = (UDPTools.BOTONES_STRUCT,mppt,luces,fan,bateria," ")
		#UDP
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
		sock.sendto(UDPTools.s_dataBotones.pack(*msg), ("239.192.0.100", 4242))

	@staticmethod
	def Receive():
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind(('', 4242))
		mreq = struct.pack("=4sl", socket.inet_aton("239.192.0.100"), socket.INADDR_ANY)
		sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
		rec=sock.recv(288)
		try:
			generic=UDPTools.s_general.unpack(rec)
			if(generic[0]==UDPTools.GPS_STRUCT):
				return UDPTools.s_gps.unpack(rec)
			elif(generic[0]==UDPTools.MPPT_STRUCT):
				return UDPTools.s_dataMPPT.unpack(rec)
			elif(generic[0]==UDPTools.EXTRAMPPT_STRUCT):
				return UDPTools.s_dataExtraMPPT.unpack(rec)
			elif(generic[0]==UDPTools.BOTONES_STRUCT):
				return UDPTools.s_dataBotones.unpack(rec)
			else:
				print("[WARNING] se recivio un paquete no esperado en el grupo multicast 239.192.0.100")
				return None
		except Exception as e:
			print(len(rec))
			print("[ERROR] el paquete no se puede traducir :",e)
			return None

if __name__ == '__main__':
	import sys
	if "-s" in sys.argv[1:]:
		import time
		import random
		r = 0#random.randint(0,3)
		if(r==0):
			UDPTools.Send_GPS(-33.5333501,-70.5882452,600,10,2016,25.6)
		elif(r==1):
			UDPTools.Send_MPPT(25.5333501,1.0,18.6,1,2,3,4,20.4)
		elif(r==2):
			UDPTools.Send_EXTRA(25.5333501,20.4,1.6)
		elif(r==3):
			UDPTools.Send_BOTONES(15,1,25,1)
	else:
		while True:
			print(UDPTools.Receive())

