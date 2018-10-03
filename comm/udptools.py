import socket
import struct
import json

class UDPTools(object):
	GENERAL_STRUCT=0
	GPS_STRUCT=1
	MPPT_STRUCT=2
	EXTRAMPPT_STRUCT=3
	BOTONES_STRUCT=4
	TEMPS_STRUCT = 5
	s_general = struct.Struct('i 28s')#0
	s_gps = struct.Struct('i f f f i d')#1 TODO: revisar porque mide 36 si no tiene mucho sentido
	s_dataMPPT = struct.Struct('I H f f f H H H H f')#2
	s_dataExtraMPPT = struct.Struct('i f f f 16s')#3
	s_dataBotones = struct.Struct('i i i i i 12s')#4

	@staticmethod
	def Send_MSG(message):
		#msg = (UDPTools.GENERAL_STRUCT,message)
		#UDP
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
		sock.sendto(json.dumps({"ctx":UDPTools.GENERAL_STRUCT,"msg":message}), ("239.192.0.100", 4242))
	@staticmethod
	def Send_GPS(lat,lon,alt,err,lastUpdate):
		#msg = (UDPTools.GPS_STRUCT,lat,lon,alt,err,lastUpdate)
		msg = {'ctx':UDPTools.GPS_STRUCT,'lat':lat,'lon':lon,'alt':alt,'err':err,'lastUpdate':lastUpdate}
		#UDP
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
		sock.sendto(json.dumps(msg), ("239.192.0.100", 4242))
	@staticmethod
	def Send_MPPT(idMPPT,Vin,Iin,Vout,bulr,out,noe,undv,t):
		#msg = (UDPTools.MPPT_STRUCT,idMPPT,Vin,Iin,Vout,bulr,out,noe,undv,t)
		msg = {'ctx':UDPTools.MPPT_STRUCT,'idMPPT':idMPPT, 'Vin':Vin, 'Iin':Iin, 'Vout':Vout, 'bulr':bulr,
				'out':out, 'noe':noe, 'undv':undv, 't':t}
		#UDP
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
		sock.sendto(json.dumps(msg), ("239.192.0.100", 4242))
	@staticmethod
	def Send_EXTRA(t1,t2,corriente):
		#msg = (UDPTools.EXTRAMPPT_STRUCT,t1,t2,corriente,b" ")
		msg = {'ctx':UDPTools.EXTRAMPPT_STRUCT,'t1':t1,'t2':t2,'corriente':corriente}
		#UDP
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
		sock.sendto(json.dumps(msg), ("239.192.0.100", 4242))
	@staticmethod
	def Send_TEMPS(t1,t2,t3,t4):
		msg = {'ctx':UDPTools.TEMPS_STRUCT,'t1':t1,'t2':t2,'t3':t3,'t4':t4}
		#UDP
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
		sock.sendto(json.dumps(msg), ("239.192.0.100", 4242))
	@staticmethod
	def Send_BOTONES(mppt,luces,fan,bateria):
		#msg = (UDPTools.BOTONES_STRUCT,mppt,luces,fan,bateria,b" ")
		msg = {'ctx':UDPTools.BOTONES_STRUCT,'mppt':mppt, 'luces':luces, 'fan':fan,
				'bateria':bateria}
		#UDP
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
		sock.sendto(json.dumps(msg), ("239.192.0.100", 4242))

	@staticmethod
	def Receive(tipo=0):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		print (4242)
		sock.bind(('', 4242))
		mreq = struct.pack("=4sl", socket.inet_aton("239.192.0.100"), socket.INADDR_ANY)
		sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
		rec=sock.recv(256)
		return json.loads(rec.decode('utf-8'))
		'''
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
				print("[WARNING] se recibio un paquete no esperado en el grupo multicast 239.192.0.100")
				return generic
		except Exception as e:
			print(len(rec))
			print(rec)
			print("[ERROR] el paquete no se puede traducir :",e)
			return None
		'''

if __name__ == '__main__':
	import sys
	if "-s" in sys.argv[1:]:
		import time
		import random
		r = 3#random.randint(0,4)
		if(r==0):
			UDPTools.Send_GPS(-33.5333501,-70.5882452,600,10,2016)
		elif(r==1):
			UDPTools.Send_MPPT(random.randint(1,3),25.5333501,1.0,18.6,1,0,0,1,20.4)
		elif(r==2):
			UDPTools.Send_EXTRA(25.5333501,20.4,1.6)
		elif(r==3):
			UDPTools.Send_BOTONES(15,1,25,1)
		elif(r==4):
			UDPTools.Send_TEMPS(15.0,1.0,25.0,1.0)
	else:
		while True:
			print (UDPTools.Receive())

