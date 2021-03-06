from multiprocessing import Process, Queue
import time
from udptools import UDPTools
import os

def singleton(class_):
  instances = {}
  def getinstance(*args, **kwargs):
    if class_ not in instances:
        instances[class_] = class_(*args, **kwargs)
    return instances[class_]
  return getinstance


class senderTask(object):
	"""docstring for senderTask"""
	def __init__(self,queue):
		self.q=queue
		print("Proceso de envio - Nace")
	def __del__(self):
		print("Proceso de envio - Muere")
	def run(self):
		while True:
			msg=self.q.get()
			print(msg)
			if(msg[0]=="GPS"):
				UDPTools.Send_GPS(*msg[1])
			elif(msg[0]=='MPPT'):
				UDPTools.Send_MPPT(*msg[1])
			elif(msg[0]=='EXTRA'):
				UDPTools.Send_EXTRA(*msg[1])
			elif(msg[0]=='BOTONES'):
				UDPTools.Send_BOTONES(*msg[1])
			else:
				UDPTools.Send_MSG(msg[1])

class gpsCatcherTask(object):
	"""docstring for gpsCrawler"""
	def __init__(self,queue,window=2.0):
		self.q=queue
		self.w=window
	def __del__(self):
		print("gpsCatcher Muere")
	def run(self):
		if os.name=='posix':
			while True:
				from .Gps import Gps
				try:
					gps = Gps()
					alt_ant=8849
					mode,lat,lon,alt,err,heading=gps.solicitar_ubicacion()
					if(mode==2):
						UDPTools.Send_GPS(float(lat),float(lon),float(alt),int(err),time.time())
					elif(mode==3):
						alt_ant=alt
						UDPTools.Send_GPS(float(lat),float(lon),float(alt),int(err),time.time())
				except:
					pass
		else:
			while True:
				time.sleep(self.w)
				self.q.put(('GPS',(-33.5333501,-70.5882452,600,10,2016),))

class i2cCatcherTask(object):
	"""docstring for gpsCrawler"""
	def __init__(self,queue,window=2.0):
		self.q=queue
		self.w=window
	def __del__(self):
		print("i2cCatcher Muere")
	def run(self):
		if os.name=='posix':
			while True:
				from .Paneles import Paneles
				p = Paneles()
				time.sleep(self.w/5)
				self.q.put(('MPPT',p.solicitar_datos(0x01)))
				time.sleep(self.w/4)
				self.q.put(('MPPT',p.solicitar_datos(0x02)))
				time.sleep(self.w/3)
				self.q.put(('MPPT',p.solicitar_datos(0x03)))
				time.sleep(self.w/2)
				self.q.put(('EXTRA',p.solicitar_datos(0x04)))
		else:
			while True:
				time.sleep(self.w)
				self.q.put(('MPPT',(1,25.5333501,1.0,18.6,1,0,0,1,20.4),))
				time.sleep(self.w/2)
				self.q.put(('EXTRA',(25.5333501,20.4,1.6),))
				time.sleep(self.w/3)

@singleton
class stateSender(object):
	"""docstring for stateSender"""
	def __init__(self):
		self.q = Queue()
		self.procesoSender = Process(name="Proceso {0}".format(0), target=senderTask(self.q).run)
		self.procesoGPS = Process(name="Proceso {0}".format(1), target=gpsCatcherTask(self.q).run)
		self.procesoI2C = Process(name="Proceso {0}".format(2), target=i2cCatcherTask(self.q).run)
		self.procesoSender.start()
		self.procesoGPS.start()
		self.procesoI2C.start()
		
		#self.procesoSender.join()
	def sendBotones(self,mppt,pan1,pan2,pan3,lucesAl,lucesBa,lucesEm,fan,bateria):
		#se flagea mppt
		mppt  = (0,1<<0)[mppt]|(0,1<<1)[pan1]|(0,1<<2)[pan2]|(0,1<<3)[pan3]
		#se flagea luces
		luces = (0,1<<0)[lucesAl]|(0,1<<1)[lucesBa]|(0,1<<2)[lucesEm]|(0,1<<3)[pan3]
		self.q.put(('BOTONES',(mppt,luces,fan,(0,1)[bateria],),))

	def kill(self):
		self.procesoSender.terminate()
		self.procesoGPS.terminate()
		self.procesoI2C.terminate()

if __name__ == '__main__':
	s = stateSender()
	print('press to send')
	input()
	s.sendBotones(False,True,True,False,True,False,False,125,True)
	print('press to send')
	input()
	s.sendBotones(True,True,True,True,True,False,False,125,True)
	print('press to send')
	input()
	s.sendBotones(False,True,True,False,False,True,False,125,True)
	print('press to end simulation')
	input()
	s.kill()